"""
Conversation Context Manager for Real-Time Voice Calls

Manages conversation state during active calls, including:
- Conversation history tracking
- Incremental data extraction
- Scenario switching (normal → emergency)
- Completion status monitoring
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel
from enum import Enum


class TurnRole(str, Enum):
    """Speaker role in conversation"""
    AGENT = "agent"
    USER = "user"


class ConversationTurn(BaseModel):
    """Single turn in a conversation"""
    role: TurnRole
    content: str
    timestamp: datetime
    confidence: Optional[float] = None  # Transcription confidence for user turns


class ConversationContext:
    """
    Manages conversation state during an active call

    Tracks conversation history, extracted data, and completion status
    to enable coherent multi-turn conversations and dynamic scenario switching.
    """

    def __init__(
        self,
        call_id: str,
        scenario: str,
        driver_name: Optional[str],
        load_number: Optional[str],
        phone_number: str,
        expected_route: Optional[Dict[str, Any]] = None,
        retell_call_id: Optional[str] = None,
        agent_config_id: Optional[str] = None
    ):
        self.call_id = call_id
        self.scenario = scenario  # check_in, emergency, delivery, custom
        self.driver_name = driver_name  # Can be None for test calls
        self.load_number = load_number  # Can be None for test calls
        self.phone_number = phone_number

        # Expected route for location conflict detection
        # Format: {"origin": "Barstow, CA", "destination": "Phoenix, AZ", "waypoints": ["Needles, CA", "Kingman, AZ"]}
        self.expected_route = expected_route or {}
        
        # Retell call metadata
        self.retell_call_id = retell_call_id
        self.agent_config_id = agent_config_id

        # Conversation tracking
        self.conversation_history: List[ConversationTurn] = []
        self.turn_count = 0

        # Data extraction (incremental)
        self.extracted_data: Dict[str, Any] = {}
        self.completion_status: Dict[str, bool] = {}

        # Scenario management
        self.is_emergency = False
        self.original_scenario = scenario
        self.emergency_triggered_at: Optional[int] = None

        # Response quality tracking
        self.one_word_response_count = 0
        self.low_confidence_count = 0
        self.clarification_attempts = 0

        # Location conflict tracking
        self.location_conflict_checked = False
        self.location_conflict_detected = False

        # Call control
        self.should_end_call = False
        self.end_call_reason: Optional[str] = None

    def add_turn(
        self,
        role: TurnRole,
        content: str,
        confidence: Optional[float] = None
    ):
        """Add a conversation turn"""
        turn = ConversationTurn(
            role=role,
            content=content,
            timestamp=datetime.now(),
            confidence=confidence
        )
        self.conversation_history.append(turn)
        self.turn_count += 1

        # Track response quality for user turns
        if role == TurnRole.USER:
            self._analyze_response_quality(content, confidence)

    def _analyze_response_quality(self, content: str, confidence: Optional[float]):
        """Analyze quality of user response"""
        # Check for one-word responses
        word_count = len(content.strip().split())
        if word_count <= 2:
            self.one_word_response_count += 1
        else:
            # Reset counter on good response
            self.one_word_response_count = 0

        # Check transcription confidence
        if confidence is not None and confidence < 0.7:
            self.low_confidence_count += 1
        else:
            self.low_confidence_count = 0

    def switch_to_emergency(self):
        """Switch conversation to emergency protocol"""
        if not self.is_emergency:
            self.is_emergency = True
            self.scenario = "emergency"
            self.emergency_triggered_at = self.turn_count
            self.extracted_data["emergency_detected_at_turn"] = self.turn_count

    def update_extracted_data(self, field: str, value: Any):
        """Update a single extracted data field"""
        self.extracted_data[field] = value
        self.completion_status[field] = True

    def bulk_update_extracted_data(self, data: Dict[str, Any]):
        """Update multiple extracted data fields"""
        for field, value in data.items():
            if value is not None:
                self.extracted_data[field] = value
                self.completion_status[field] = True

    def get_missing_fields(self, required_fields: List[str]) -> List[str]:
        """Get list of required fields not yet collected"""
        return [
            field for field in required_fields
            if not self.completion_status.get(field, False)
        ]

    def is_complete(self, required_fields: List[str]) -> bool:
        """Check if all required fields have been collected"""
        return len(self.get_missing_fields(required_fields)) == 0

    def should_probe_for_detail(self) -> bool:
        """Check if agent should probe for more detail"""
        return 3 <= self.one_word_response_count < 5

    def should_end_due_to_unresponsiveness(self) -> bool:
        """Check if call should end due to unresponsive driver"""
        return self.one_word_response_count >= 5

    def should_clarify(self) -> bool:
        """Check if agent should ask for clarification"""
        return self.low_confidence_count > 0 and self.clarification_attempts < 3

    def should_escalate_due_to_noise(self) -> bool:
        """Check if call should escalate due to persistent noise"""
        return self.clarification_attempts >= 3

    def request_clarification(self):
        """Mark that a clarification was requested"""
        self.clarification_attempts += 1

    def mark_for_end(self, reason: str):
        """Mark call to be ended"""
        self.should_end_call = True
        self.end_call_reason = reason

    def should_check_location_conflict(self) -> bool:
        """Check if we should verify the driver's stated location against expected route"""
        # Only check once per call, and only if we have route data and a stated location
        if self.location_conflict_checked:
            return False
        if not self.expected_route:
            return False
        stated_location = self.extracted_data.get("current_location")
        return stated_location is not None

    def mark_location_conflict_checked(self, conflict_detected: bool = False):
        """Mark that we've checked for location conflict"""
        self.location_conflict_checked = True
        self.location_conflict_detected = conflict_detected

    def get_conversation_for_llm(self, max_turns: int = 10) -> List[Dict[str, str]]:
        """
        Get recent conversation history formatted for LLM

        Returns list of messages in format:
        [{"role": "assistant", "content": "..."}, {"role": "user", "content": "..."}]
        """
        recent_turns = self.conversation_history[-max_turns:] if max_turns else self.conversation_history

        messages = []
        for turn in recent_turns:
            messages.append({
                "role": "assistant" if turn.role == TurnRole.AGENT else "user",
                "content": turn.content
            })

        return messages

    def get_context_summary(self) -> Dict[str, Any]:
        """Get summary of current context for debugging/logging"""
        return {
            "call_id": self.call_id,
            "scenario": self.scenario,
            "is_emergency": self.is_emergency,
            "turn_count": self.turn_count,
            "extracted_fields": list(self.extracted_data.keys()),
            "one_word_responses": self.one_word_response_count,
            "low_confidence_count": self.low_confidence_count,
            "clarification_attempts": self.clarification_attempts,
            "should_end_call": self.should_end_call,
            "end_call_reason": self.end_call_reason
        }


class ContextManager:
    """
    Manages multiple active conversation contexts

    In-memory storage of active call contexts (could be Redis in production)
    """

    def __init__(self):
        self._contexts: Dict[str, ConversationContext] = {}

    def create_context(
        self,
        call_id: str,
        scenario: str,
        driver_name: Optional[str],
        load_number: Optional[str],
        phone_number: str,
        expected_route: Optional[Dict[str, Any]] = None,
        retell_call_id: Optional[str] = None,
        agent_config_id: Optional[str] = None
    ) -> ConversationContext:
        """Create new conversation context"""
        context = ConversationContext(
            call_id=call_id,
            scenario=scenario,
            driver_name=driver_name,
            load_number=load_number,
            phone_number=phone_number,
            expected_route=expected_route,
            retell_call_id=retell_call_id,
            agent_config_id=agent_config_id
        )
        self._contexts[call_id] = context
        return context

    def get_context(self, call_id: str) -> Optional[ConversationContext]:
        """Get existing conversation context"""
        return self._contexts.get(call_id)

    def remove_context(self, call_id: str):
        """Remove conversation context when call ends"""
        if call_id in self._contexts:
            del self._contexts[call_id]

    def get_all_active_contexts(self) -> List[str]:
        """Get list of all active call IDs"""
        return list(self._contexts.keys())


# Global context manager instance
_context_manager = ContextManager()


def get_context_manager() -> ContextManager:
    """Get global context manager instance"""
    return _context_manager
