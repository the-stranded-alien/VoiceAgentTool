"""
Real-Time LLM Response Generator for Voice Calls

Generates dynamic responses during active calls using Claude API.
Handles conversation flow, emergency detection, and edge cases.
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from app.services.llm.base import LLMClient
from app.services.llm.prompts import (
    PromptTemplates,
    CHECK_IN_SYSTEM_PROMPT,
    EMERGENCY_SYSTEM_PROMPT
)
from app.services.llm.context import ConversationContext, TurnRole
from app.services.llm.extractor import StructuredDataExtractor

logger = logging.getLogger(__name__)


# Emergency trigger keywords
EMERGENCY_KEYWORDS = [
    "accident", "crash", "blowout", "breakdown",
    "medical", "emergency", "injured", "hurt",
    "pulling over", "can't drive", "need help",
    "hospital", "ambulance", "collision", "wreck"
]

# Sample route data for location conflict detection (mock data for demo)
# In production, this would come from a TMS/routing system
MOCK_ROUTE_DATA = {
    # Barstow to Phoenix route
    "7891-B": {
        "origin": "Barstow, CA",
        "destination": "Phoenix, AZ",
        "expected_corridor": ["Barstow", "Needles", "Kingman", "Phoenix", "I-40", "I-10", "California", "Arizona"],
        "off_route_indicators": ["San Diego", "Los Angeles", "Las Vegas", "Salt Lake", "Denver", "Texas", "New Mexico"]
    },
    # Default route pattern
    "default": {
        "origin": "Origin",
        "destination": "Destination",
        "expected_corridor": [],
        "off_route_indicators": []
    }
}


def get_route_for_load(load_number: str) -> Dict[str, Any]:
    """Get expected route data for a load number"""
    # Check for exact match first
    if load_number in MOCK_ROUTE_DATA:
        return MOCK_ROUTE_DATA[load_number]
    # Check for partial match (e.g., "7891-B" matches load containing "7891")
    for key in MOCK_ROUTE_DATA:
        if key != "default" and key in load_number:
            return MOCK_ROUTE_DATA[key]
    return MOCK_ROUTE_DATA["default"]


class RealtimeLLMHandler:
    """
    Handles real-time LLM response generation during voice calls

    Responsible for:
    - Generating contextually appropriate responses
    - Detecting emergencies mid-call
    - Handling edge cases (uncooperative, noisy, conflicts)
    - Managing conversation flow and completion
    """

    def __init__(self):
        self.llm_client = LLMClient()
        self.extractor = StructuredDataExtractor()

    def detect_emergency(self, text: str) -> bool:
        """
        Detect if text contains emergency keywords

        Args:
            text: User's speech text

        Returns:
            True if emergency detected
        """
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in EMERGENCY_KEYWORDS)

    def detect_location_conflict(self, stated_location: str, expected_route: Dict[str, Any]) -> bool:
        """
        Detect if the driver's stated location conflicts with expected route

        Uses simple keyword matching against expected corridor and off-route indicators.
        In production, this would use geo-fencing or actual coordinates.

        Args:
            stated_location: Location the driver claimed
            expected_route: Route data with expected_corridor and off_route_indicators

        Returns:
            True if location appears to conflict with expected route
        """
        if not stated_location or not expected_route:
            return False

        stated_lower = stated_location.lower()
        expected_corridor = expected_route.get("expected_corridor", [])
        off_route_indicators = expected_route.get("off_route_indicators", [])

        # Check if any off-route indicator is mentioned
        for indicator in off_route_indicators:
            if indicator.lower() in stated_lower:
                logger.info(f"Location conflict detected: '{stated_location}' contains off-route indicator '{indicator}'")
                return True

        # If we have expected corridor data, check if location is on route
        if expected_corridor:
            on_route = any(waypoint.lower() in stated_lower for waypoint in expected_corridor)
            if not on_route:
                # Only flag as conflict if we're confident they're off-route
                # (i.e., they mentioned a specific location that's not on the route)
                has_specific_location = any(word in stated_lower for word in ["near", "at", "in", "on", "exit", "mile"])
                if has_specific_location:
                    logger.info(f"Location conflict: '{stated_location}' not on expected route {expected_corridor}")
                    return True

        return False

    async def generate_response(
        self,
        context: ConversationContext,
        user_utterance: str,
        confidence: Optional[float] = None
    ) -> Tuple[str, bool]:
        """
        Generate agent response for current conversation turn

        Args:
            context: Current conversation context
            user_utterance: What the driver just said
            confidence: Transcription confidence score (0-1)

        Returns:
            Tuple of (response_text, should_end_call)
        """
        # Add user turn to context
        context.add_turn(TurnRole.USER, user_utterance, confidence)

        # Check for emergency trigger (immediate switch)
        if not context.is_emergency and self.detect_emergency(user_utterance):
            logger.info(f"Emergency detected in call {context.call_id} - switching to emergency protocol")
            context.switch_to_emergency()
            # Set call_outcome immediately
            context.update_extracted_data("call_outcome", "Emergency Escalation")
            response = self._generate_emergency_acknowledgment()
            context.add_turn(TurnRole.AGENT, response)
            return response, False

        # Handle edge cases
        edge_case_response = self._handle_edge_cases(context, user_utterance, confidence)
        if edge_case_response:
            context.add_turn(TurnRole.AGENT, edge_case_response)
            return edge_case_response, context.should_end_call

        # Generate normal conversational response
        response = await self._generate_conversational_response(context, user_utterance)
        context.add_turn(TurnRole.AGENT, response)

        # Extract data incrementally
        await self._extract_data_incrementally(context, user_utterance)

        # Check if conversation should end
        should_end = self._should_end_conversation(context)
        if should_end:
            context.mark_for_end("conversation_complete")
            # For emergency calls, replace response with escalation message
            if context.is_emergency:
                escalation_msg = self.generate_final_response(context)
                # Replace the last agent turn with escalation message
                if context.conversation_history:
                    context.conversation_history[-1].content = escalation_msg
                return escalation_msg, True

        return response, should_end

    def _generate_emergency_acknowledgment(self) -> str:
        """Generate immediate emergency acknowledgment"""
        return "I understand, let me help you. Is everyone safe?"

    def _handle_edge_cases(
        self,
        context: ConversationContext,
        user_utterance: str,
        confidence: Optional[float]
    ) -> Optional[str]:
        """
        Handle edge cases (uncooperative driver, noisy environment, conflicting location, etc.)

        Returns:
            Response text if edge case handled, None otherwise
        """
        # Check for unresponsiveness
        if context.should_end_due_to_unresponsiveness():
            logger.info(f"Call {context.call_id}: Ending due to unresponsive driver")
            context.mark_for_end("unresponsive_driver")
            return "I'll let you go for now. Please call dispatch back when you have a moment. Drive safe!"

        # Check if should probe for more detail
        if context.should_probe_for_detail():
            logger.info(f"Call {context.call_id}: Probing for more detail (attempt {context.one_word_response_count})")
            return self._generate_probing_response(context)

        # Check for low confidence (noisy environment)
        if context.should_escalate_due_to_noise():
            logger.info(f"Call {context.call_id}: Escalating due to persistent noise")
            context.mark_for_end("poor_connection")
            return "I'm having trouble hearing you clearly. Let me have a human dispatcher call you back on a better line."

        if context.should_clarify():
            context.request_clarification()
            logger.info(f"Call {context.call_id}: Requesting clarification (attempt {context.clarification_attempts})")
            return "I didn't quite catch that. Could you repeat that for me?"

        # Check for location conflict (only once per call, non-confrontational)
        if context.should_check_location_conflict():
            stated_location = context.extracted_data.get("current_location")
            if stated_location:
                conflict = self.detect_location_conflict(stated_location, context.expected_route)
                context.mark_location_conflict_checked(conflict)
                if conflict:
                    logger.info(f"Call {context.call_id}: Location conflict detected, asking for verification")
                    expected_area = context.expected_route.get("destination", "the expected area")
                    return self._generate_location_verification_response(context, expected_area)

        return None

    def _generate_location_verification_response(self, context: ConversationContext, expected_area: str) -> str:
        """
        Generate a non-confrontational response to verify the driver's location

        Per requirements: handle discrepancies in a non-confrontational way
        """
        origin = context.expected_route.get("origin", "")
        destination = context.expected_route.get("destination", "")

        if origin and destination:
            return f"Just to make sure I have this right - you're on the route from {origin} to {destination}, correct? The system shows a slightly different area."
        else:
            return "Just double-checking the location - the system is showing you might be in a different area. Does that sound about right?"

    def _generate_probing_response(self, context: ConversationContext) -> str:
        """Generate response to probe for more detail from uncooperative driver"""
        if context.one_word_response_count == 3:
            return "I need a bit more detail to update the system. Can you give me a few more specifics?"
        elif context.one_word_response_count == 4:
            return "I know you're busy, but I just need a little more information real quick."
        return "Could you elaborate on that a bit?"

    async def _generate_conversational_response(
        self,
        context: ConversationContext,
        user_utterance: str
    ) -> str:
        """
        Generate contextually appropriate conversational response

        Uses Claude to generate natural, scenario-appropriate responses
        """
        try:
            # Get appropriate system prompt
            system_prompt = PromptTemplates.get_scenario_system_prompt(
                scenario=context.scenario,
                is_emergency=context.is_emergency
            )

            # Format with driver info - handle None values for test calls
            driver_name_str = context.driver_name if context.driver_name else "[Driver name not provided - ask for it]"
            load_number_str = context.load_number if context.load_number else "[Load number not provided - ask for it]"
            system_prompt = system_prompt.replace("{driver_name}", driver_name_str)
            system_prompt = system_prompt.replace("{load_number}", load_number_str)

            # Add context about what info we still need
            missing_info_hint = self._get_missing_info_hint(context)
            if missing_info_hint:
                system_prompt += f"\n\nCURRENT STATUS: {missing_info_hint}"

            # Build conversation history for context
            conversation_msgs = context.get_conversation_for_llm(max_turns=6)

            # Create messages for Claude
            messages = []

            # Add conversation history
            if conversation_msgs:
                messages.extend(conversation_msgs)

            # Add current user utterance
            messages.append({
                "role": "user",
                "content": user_utterance
            })

            # Generate response
            response = await self.llm_client.generate_text(
                prompt="",  # Empty prompt since we're using messages
                messages=messages,
                system_prompt=system_prompt,
                max_tokens=150,  # Keep responses short
                temperature=0.7  # Slight creativity for naturalness
            )

            # Clean up response (remove any meta-commentary)
            response = self._clean_response(response)

            return response

        except Exception as e:
            logger.error(f"Error generating response for call {context.call_id}: {e}", exc_info=True)
            # Fallback response
            return self._get_fallback_response(context)

    def _get_missing_info_hint(self, context: ConversationContext) -> str:
        """
        Generate hint about what information is still needed

        This guides the LLM to ask appropriate follow-up questions
        """
        if context.is_emergency:
            missing = []
            # Priority order: safety first, then location, then type, then load security, then injury details
            if not context.extracted_data.get("safety_status"):
                missing.append("safety status (is everyone safe?)")
            if not context.extracted_data.get("emergency_location"):
                missing.append("exact location")
            if not context.extracted_data.get("emergency_type"):
                missing.append("emergency type (accident, breakdown, medical, other)")
            if not context.extracted_data.get("load_secure"):
                missing.append("load security (is the load secure?)")
            if not context.extracted_data.get("injury_status"):
                missing.append("injury status")

            if missing:
                return f"CRITICAL: Still need to ask about: {', '.join(missing[:3])}"  # Limit to top 3 priorities

        elif context.scenario == "check_in":
            driver_status = context.extracted_data.get("driver_status")

            if not driver_status:
                return "Need to determine driver's current status first"

            missing = []

            if driver_status == "Driving":
                if not context.extracted_data.get("current_location"):
                    missing.append("current location")
                if not context.extracted_data.get("eta"):
                    missing.append("ETA")
                if not context.extracted_data.get("delay_reason"):
                    missing.append("any delays or issues")

            elif driver_status in ["Arrived", "Unloading"]:
                if not context.extracted_data.get("unloading_status"):
                    missing.append("unloading status/door number")
                if not context.extracted_data.get("pod_reminder_acknowledged"):
                    missing.append("POD reminder")

            elif driver_status == "Delayed":
                if not context.extracted_data.get("current_location"):
                    missing.append("current location")
                if not context.extracted_data.get("delay_reason"):
                    missing.append("reason for delay")
                if not context.extracted_data.get("eta"):
                    missing.append("new ETA")

            if missing:
                return f"Still need to ask about: {', '.join(missing)}"

        return ""

    def _clean_response(self, response: str) -> str:
        """Clean up LLM response to remove meta-commentary"""
        # Remove any "Agent:", "Dispatcher:", etc. prefixes
        response = re.sub(r'^(Agent|Dispatcher):\s*', '', response, flags=re.IGNORECASE)

        # Remove quotes if the entire response is quoted
        if response.startswith('"') and response.endswith('"'):
            response = response[1:-1]

        return response.strip()

    def _get_fallback_response(self, context: ConversationContext) -> str:
        """Get fallback response if LLM fails"""
        if context.is_emergency:
            return "Can you tell me your exact location?"
        else:
            return "Got it. Anything else I should know?"

    def _detect_pod_acknowledgment(self, agent_message: str, user_response: str) -> bool:
        """
        Detect if driver acknowledged POD reminder

        Looks for POD reminder in agent message and positive acknowledgment in user response
        """
        # Check if agent mentioned POD
        pod_keywords = ["pod", "proof of delivery", "paperwork", "documentation"]
        agent_lower = agent_message.lower()
        has_pod_mention = any(keyword in agent_lower for keyword in pod_keywords)

        if not has_pod_mention:
            return False

        # Check for positive acknowledgment in user response
        positive_keywords = [
            "ok", "okay", "sure", "yes", "yeah", "yep", "got it",
            "will do", "no problem", "understood", "sounds good", "alright"
        ]
        user_lower = user_response.lower()
        has_acknowledgment = any(keyword in user_lower for keyword in positive_keywords)

        return has_acknowledgment

    async def _extract_data_incrementally(
        self,
        context: ConversationContext,
        user_utterance: str
    ):
        """
        Extract structured data from user utterance and update context

        Performs incremental extraction so we track what's been collected
        """
        try:
            # Check for POD acknowledgment (special case)
            if len(context.conversation_history) >= 2:
                last_agent_message = None
                for turn in reversed(context.conversation_history):
                    if turn.role == TurnRole.AGENT:
                        last_agent_message = turn.content
                        break

                if last_agent_message:
                    if self._detect_pod_acknowledgment(last_agent_message, user_utterance):
                        context.update_extracted_data("pod_reminder_acknowledged", True)
                        logger.debug(f"Call {context.call_id}: POD reminder acknowledged")

            # Build conversation excerpt for extraction
            recent_turns = context.get_conversation_for_llm(max_turns=4)
            conversation_text = "\n".join([
                f"{msg['role'].title()}: {msg['content']}"
                for msg in recent_turns
            ])

            # Extract based on scenario
            if context.is_emergency:
                # Emergency data extraction
                extracted = await self.extractor.extract_from_transcript(
                    transcript=conversation_text,
                    scenario_type="emergency",
                    driver_name=context.driver_name,
                    load_number=context.load_number
                )
            else:
                # Check-in data extraction
                extracted = await self.extractor.extract_from_transcript(
                    transcript=conversation_text,
                    scenario_type="check_in",
                    driver_name=context.driver_name,
                    load_number=context.load_number
                )

            # Update context with extracted data
            if extracted:
                context.bulk_update_extracted_data(extracted)
                logger.debug(f"Call {context.call_id}: Extracted data - {extracted}")

        except Exception as e:
            logger.error(f"Error extracting data for call {context.call_id}: {e}")

    def _should_end_conversation(self, context: ConversationContext) -> bool:
        """
        Determine if conversation should end

        Args:
            context: Current conversation context

        Returns:
            True if call should end
        """
        # Emergency calls end after gathering critical info
        if context.is_emergency:
            # Required emergency fields per problem statement:
            # - emergency_type: "Accident" OR "Breakdown" OR "Medical" OR "Other"
            # - safety_status: (e.g., "Driver confirmed everyone is safe")
            # - injury_status: (e.g., "No injuries reported")
            # - emergency_location: (e.g., "I-15 North, Mile Marker 123")
            # - load_secure: true OR false
            # - escalation_status: "Connected to Human Dispatcher"
            
            has_type = context.extracted_data.get("emergency_type") is not None
            has_safety = context.extracted_data.get("safety_status") is not None
            has_injury = context.extracted_data.get("injury_status") is not None
            has_location = context.extracted_data.get("emergency_location") is not None
            has_load_secure = context.extracted_data.get("load_secure") is not None

            # End if we have all critical emergency information
            # Minimum required: type, safety, location, and load_secure
            if has_type and has_safety and has_location and has_load_secure:
                # Set escalation status before ending
                context.update_extracted_data("escalation_status", "Connected to Human Dispatcher")
                context.update_extracted_data("call_outcome", "Emergency Escalation")
                return True

            # Also end if too many turns in emergency (shouldn't take long)
            # But still try to get minimum info (type, safety, location)
            if context.turn_count > 12:  # ~6 exchanges
                # If we have minimum critical info, end the call
                if has_type and has_safety and has_location:
                    context.update_extracted_data("escalation_status", "Connected to Human Dispatcher")
                    context.update_extracted_data("call_outcome", "Emergency Escalation")
                    return True
                # Otherwise, end anyway but mark as incomplete
                context.update_extracted_data("escalation_status", "Connected to Human Dispatcher")
                context.update_extracted_data("call_outcome", "Emergency Escalation")
                return True

        # Normal check-in calls
        elif context.scenario == "check_in":
            # Determine required fields based on driver status
            driver_status = context.extracted_data.get("driver_status")

            if driver_status == "Driving":
                # For driving: need location, ETA, delay info
                required = ["driver_status", "current_location", "eta"]
                optional_asked = context.turn_count >= 6  # Asked about delays/issues
                if context.is_complete(required) and optional_asked:
                    return True

            elif driver_status in ["Arrived", "Unloading"]:
                # For arrived: need POD reminder acknowledged
                # If POD is acknowledged and we have driver_status, consider it complete
                # (current_location and unloading_status are nice-to-have but not always necessary)
                has_pod_acknowledged = context.extracted_data.get("pod_reminder_acknowledged") is True
                if has_pod_acknowledged and context.turn_count >= 6:
                    # If we have POD acknowledged and enough conversation, end the call
                    return True
                
                # Also check if we have all required fields (strict check)
                required = ["driver_status", "current_location", "unloading_status", "pod_reminder_acknowledged"]
                if context.is_complete(required):
                    return True

            elif driver_status == "Delayed":
                # For delayed: need location, reason, new ETA
                required = ["driver_status", "current_location", "delay_reason", "eta"]
                if context.is_complete(required):
                    return True

            # End if conversation is too long (natural limit)
            if context.turn_count > 20:  # ~10 exchanges
                return True

            # End if we have call_outcome set (indicates completion)
            if context.extracted_data.get("call_outcome"):
                # Give a couple more turns for POD reminder if needed
                if context.turn_count >= 8:
                    return True

        return False

    def generate_final_response(self, context: ConversationContext) -> str:
        """
        Generate final response before ending call

        Args:
            context: Conversation context

        Returns:
            Final closing statement
        """
        if context.is_emergency:
            # Per problem statement: "I'm connecting you to a human dispatcher now."
            return "I'm connecting you to a human dispatcher now who will coordinate help."
        elif context.end_call_reason == "unresponsive_driver":
            return "I'll let you go for now. Please call dispatch back when you have a moment. Drive safe!"
        elif context.end_call_reason == "poor_connection":
            return "I'm having trouble hearing you. A dispatcher will call you back shortly."
        else:
            # Normal completion
            driver_name = context.driver_name if context.driver_name else ""
            if driver_name:
                return f"Perfect. Thanks for the update, {driver_name}. Drive safe!"
            else:
                return "Perfect. Thanks for the update. Drive safe!"


# Global instance
_realtime_handler = RealtimeLLMHandler()


def get_realtime_handler() -> RealtimeLLMHandler:
    """Get global realtime handler instance"""
    return _realtime_handler
