"""
WebSocket Endpoint for Retell AI Custom LLM Integration

This endpoint receives real-time requests from Retell AI during active calls
and returns LLM-generated responses for natural conversation.
"""

import logging
import json
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.llm.context import get_context_manager, TurnRole
from app.services.llm.realtime import get_realtime_handler
from app.database import get_supabase
from app.services.call_service import CallService

logger = logging.getLogger(__name__)

router = APIRouter()


class RetellWebSocketHandler:
    """
    Handles Retell AI WebSocket communication

    Message Flow:
    1. Retell sends call_details (at start)
    2. Retell sends response_required (during conversation)
    3. Backend responds with agent's reply
    4. Repeat until call ends
    """

    def __init__(self):
        self.context_manager = get_context_manager()
        self.realtime_handler = get_realtime_handler()

    async def handle_connection(self, websocket: WebSocket):
        """
        Handle WebSocket connection lifecycle

        Args:
            websocket: FastAPI WebSocket connection
        """
        await websocket.accept()
        logger.info("WebSocket connection established")

        call_id = None

        try:
            while True:
                # Receive message from Retell
                data = await websocket.receive_text()
                message = json.loads(data)

                logger.debug(f"Received from Retell: {message}")

                # Handle different message types
                response = await self._handle_message(message)

                if response:
                    # Send response back to Retell
                    await websocket.send_text(json.dumps(response))
                    logger.debug(f"Sent to Retell: {response}")

                # Check if we should end the call
                if response and response.get("end_call", False):
                    logger.info(f"Ending call {call_id}")
                    break

        except WebSocketDisconnect:
            logger.info("WebSocket disconnected")
        except Exception as e:
            logger.error(f"WebSocket error: {e}", exc_info=True)
        finally:
            # Cleanup context when call ends
            if call_id:
                self.context_manager.remove_context(call_id)
                logger.info(f"Cleaned up context for call {call_id}")

    async def _handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming message from Retell

        Args:
            message: Message dict from Retell

        Returns:
            Response dict to send back to Retell
        """
        interaction_type = message.get("interaction_type")

        if interaction_type == "call_details":
            return await self._handle_call_details(message)

        elif interaction_type == "response_required":
            return await self._handle_response_required(message)

        elif interaction_type == "reminder_required":
            return await self._handle_reminder_required(message)

        elif interaction_type == "update_only":
            # Just an update, no response needed
            return None

        else:
            logger.warning(f"Unknown interaction type: {interaction_type}")
            return None

    async def _handle_call_details(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle call_details message (sent at call start)

        Creates conversation context and sends initial greeting

        Message structure from Retell:
        {
            "interaction_type": "call_details",
            "call_id": "...",
            "retell_llm_dynamic_variables": {
                "driver_name": "...",
                "load_number": "...",
                "call_id": "...",  # Our internal call ID
                "scenario": "..."
            }
        }
        """
        logger.info("Handling call_details message")

        retell_call_id = message.get("call_id")
        variables = message.get("retell_llm_dynamic_variables", {})

        # Extract call info
        internal_call_id = variables.get("call_id", retell_call_id)
        driver_name = variables.get("driver_name", "Driver")
        load_number = variables.get("load_number", "Unknown")
        phone_number = variables.get("phone_number", "Unknown")
        scenario = variables.get("scenario", "check_in")

        logger.info(f"Call details - ID: {internal_call_id}, Driver: {driver_name}, Load: {load_number}, Scenario: {scenario}")

        # Create conversation context
        context = self.context_manager.create_context(
            call_id=internal_call_id,
            scenario=scenario,
            driver_name=driver_name,
            load_number=load_number,
            phone_number=phone_number
        )

        # Generate opening greeting
        opening_message = self._generate_opening(context)
        context.add_turn(TurnRole.AGENT, opening_message)

        # Return first response
        return {
            "response_type": "response",
            "response_id": 0,
            "content": opening_message,
            "content_complete": True,
            "end_call": False
        }

    def _generate_opening(self, context) -> str:
        """Generate opening greeting based on scenario"""
        if context.scenario == "emergency":
            return f"This is Dispatch calling about an emergency. {context.driver_name}, are you able to talk?"
        else:
            return f"Hi {context.driver_name}, this is Dispatch with a check call on load {context.load_number}. Can you give me an update on your status?"

    async def _handle_response_required(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle response_required message (main conversation turns)

        Message structure from Retell:
        {
            "interaction_type": "response_required",
            "response_id": 1,
            "transcript": [
                {"role": "agent", "content": "..."},
                {"role": "user", "content": "..."}
            ]
        }
        """
        response_id = message.get("response_id", 0)
        transcript = message.get("transcript", [])

        if not transcript:
            logger.warning("No transcript provided in response_required")
            return self._error_response(response_id)

        # Get last user utterance
        last_user_turn = None
        for turn in reversed(transcript):
            if turn.get("role") == "user":
                last_user_turn = turn
                break

        if not last_user_turn:
            logger.warning("No user turn found in transcript")
            return self._error_response(response_id)

        user_utterance = last_user_turn.get("content", "")

        # Try to extract call ID from transcript or context
        # Retell doesn't always include call_id in response_required
        # We need to match based on active contexts
        # For now, use the first (and likely only) active context
        active_contexts = self.context_manager.get_all_active_contexts()
        if not active_contexts:
            logger.error("No active contexts found")
            return self._error_response(response_id)

        call_id = active_contexts[0]  # In production, need better matching
        context = self.context_manager.get_context(call_id)

        if not context:
            logger.error(f"Context not found for call {call_id}")
            return self._error_response(response_id)

        # Generate response using realtime handler
        agent_response, should_end = await self.realtime_handler.generate_response(
            context=context,
            user_utterance=user_utterance,
            confidence=None  # Retell doesn't provide this in transcript
        )

        # If should end, generate final response
        if should_end:
            final_response = self.realtime_handler.generate_final_response(context)
            agent_response = final_response

        logger.info(f"Call {call_id}: User said '{user_utterance}', Agent responding '{agent_response}'")

        return {
            "response_type": "response",
            "response_id": response_id,
            "content": agent_response,
            "content_complete": True,
            "end_call": should_end
        }

    async def _handle_reminder_required(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle reminder_required message (when user is silent too long)

        This can be used to prompt the user if they haven't spoken in a while
        """
        response_id = message.get("response_id", 0)

        # Get active context
        active_contexts = self.context_manager.get_all_active_contexts()
        if not active_contexts:
            return self._error_response(response_id)

        call_id = active_contexts[0]
        context = self.context_manager.get_context(call_id)

        if not context:
            return self._error_response(response_id)

        # Generate a gentle prompt
        if context.is_emergency:
            reminder = "Are you still there? Can you hear me?"
        else:
            reminder = f"{context.driver_name}, are you still there?"

        context.add_turn(TurnRole.AGENT, reminder)

        return {
            "response_type": "response",
            "response_id": response_id,
            "content": reminder,
            "content_complete": True,
            "end_call": False
        }

    def _error_response(self, response_id: int) -> Dict[str, Any]:
        """Generate error response"""
        return {
            "response_type": "response",
            "response_id": response_id,
            "content": "I'm having technical difficulties. Let me have a dispatcher call you back.",
            "content_complete": True,
            "end_call": True
        }


# Global handler instance
_ws_handler = RetellWebSocketHandler()


@router.websocket("/llm")
async def retell_llm_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for Retell AI Custom LLM

    Retell will connect to: ws://your-domain/ws/llm

    This endpoint handles real-time conversation during calls
    """
    await _ws_handler.handle_connection(websocket)
