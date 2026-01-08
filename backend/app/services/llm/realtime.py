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

    def generate_response(
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
            logger.info(f"Emergency detected in call {context.call_id}")
            context.switch_to_emergency()
            response = self._generate_emergency_acknowledgment()
            context.add_turn(TurnRole.AGENT, response)
            return response, False

        # Handle edge cases
        edge_case_response = self._handle_edge_cases(context, user_utterance, confidence)
        if edge_case_response:
            context.add_turn(TurnRole.AGENT, edge_case_response)
            return edge_case_response, context.should_end_call

        # Generate normal conversational response
        response = self._generate_conversational_response(context, user_utterance)
        context.add_turn(TurnRole.AGENT, response)

        # Extract data incrementally
        self._extract_data_incrementally(context, user_utterance)

        # Check if conversation should end
        should_end = self._should_end_conversation(context)
        if should_end:
            context.mark_for_end("conversation_complete")

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
        Handle edge cases (uncooperative driver, noisy environment, etc.)

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

        return None

    def _generate_probing_response(self, context: ConversationContext) -> str:
        """Generate response to probe for more detail from uncooperative driver"""
        if context.one_word_response_count == 3:
            return "I need a bit more detail to update the system. Can you give me a few more specifics?"
        elif context.one_word_response_count == 4:
            return "I know you're busy, but I just need a little more information real quick."
        return "Could you elaborate on that a bit?"

    def _generate_conversational_response(
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

            # Format with driver info
            system_prompt = system_prompt.replace("{driver_name}", context.driver_name)
            system_prompt = system_prompt.replace("{load_number}", context.load_number)

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
            response = self.llm_client.generate_text(
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

    def _extract_data_incrementally(
        self,
        context: ConversationContext,
        user_utterance: str
    ):
        """
        Extract structured data from user utterance and update context

        Performs incremental extraction so we track what's been collected
        """
        try:
            # Build conversation excerpt for extraction
            recent_turns = context.get_conversation_for_llm(max_turns=4)
            conversation_text = "\n".join([
                f"{msg['role'].title()}: {msg['content']}"
                for msg in recent_turns
            ])

            # Extract based on scenario
            if context.is_emergency:
                # Emergency data extraction
                extracted = self.extractor.extract_from_transcript(
                    transcript=conversation_text,
                    scenario_type="emergency",
                    driver_name=context.driver_name,
                    load_number=context.load_number
                )
            else:
                # Check-in data extraction
                extracted = self.extractor.extract_from_transcript(
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
        # Emergency calls end after escalation statement
        if context.is_emergency:
            # Check if we've gathered critical emergency info
            critical_fields = ["emergency_type", "safety_status", "emergency_location"]
            if context.is_complete(critical_fields):
                return True

        # Normal calls end when all info gathered or too many turns
        if context.scenario == "check_in":
            # Don't force completion, let it be natural
            # But end if conversation is going too long
            if context.turn_count > 20:  # ~10 exchanges
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
            return "I'm connecting you to a human dispatcher now who will coordinate help."
        elif context.end_call_reason == "unresponsive_driver":
            return "I'll let you go for now. Please call dispatch back when you have a moment. Drive safe!"
        elif context.end_call_reason == "poor_connection":
            return "I'm having trouble hearing you. A dispatcher will call you back shortly."
        else:
            # Normal completion
            return f"Perfect. Thanks for the update, {context.driver_name}. Drive safe!"


# Global instance
_realtime_handler = RealtimeLLMHandler()


def get_realtime_handler() -> RealtimeLLMHandler:
    """Get global realtime handler instance"""
    return _realtime_handler
