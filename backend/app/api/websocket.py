"""
WebSocket Endpoint for Retell AI Custom LLM Integration

This endpoint receives real-time requests from Retell AI during active calls
and returns LLM-generated responses for natural conversation.
"""

import logging
import json
import time
import asyncio
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

    async def handle_connection(self, websocket: WebSocket, retell_call_id: str = None):
        """
        Handle WebSocket connection lifecycle

        Args:
            websocket: FastAPI WebSocket connection
            retell_call_id: Optional Retell call ID from URL path
        """
        await websocket.accept()

        call_id = None
        context_created = False
        current_retell_call_id = retell_call_id
        opening_sent = False

        try:
            # Always use the last created call with "initiated" status
            if not context_created:
                call_id = await self._create_context_from_retell_id(current_retell_call_id)
                if call_id:
                    context_created = True
                    context = self.context_manager.get_context(call_id)
                    if context:
                        # Generate and send opening message proactively
                        opening_message = self._generate_opening(context)
                        context.add_turn(TurnRole.AGENT, opening_message)
                        
                        opening_response = {
                            "response_type": "response",
                            "response_id": 0,
                            "content": opening_message,
                            "content_complete": True,
                            "end_call": False
                        }
                        
                        await websocket.send_text(json.dumps(opening_response))
                        opening_sent = True

            while True:
                try:
                    message_data = await asyncio.wait_for(websocket.receive(), timeout=30.0)
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error receiving message: {e}")
                    break
                
                # Handle different message types
                if message_data.get("type") == "websocket.receive":
                    if "text" in message_data:
                        data = message_data["text"]
                    elif "bytes" in message_data:
                        data = message_data["bytes"].decode('utf-8')
                    else:
                        continue
                elif message_data.get("type") == "websocket.disconnect":
                    break
                else:
                    continue
                    
                try:
                    message = json.loads(data)
                except json.JSONDecodeError:
                    continue

                interaction_type = message.get('interaction_type')
                
                # Extract retell_call_id from message if available
                if not current_retell_call_id:
                    current_retell_call_id = message.get("call_id")

                # Handle different message types
                response = await self._handle_message(message)

                # Extract call_id from call_details message if not already set
                if call_id is None and message.get("interaction_type") == "call_details":
                    variables = message.get("retell_llm_dynamic_variables", {})
                    call_id = variables.get("call_id", message.get("call_id"))
                    context_created = True
                    
                    # Update context with retell_call_id if we have it
                    if current_retell_call_id and call_id:
                        context = self.context_manager.get_context(call_id)
                        if context:
                            context.retell_call_id = current_retell_call_id
                            
                            # Update context with values from dynamic variables if they differ
                            new_driver_name = variables.get("driver_name")
                            new_load_number = variables.get("load_number")
                            if new_driver_name and new_driver_name != context.driver_name:
                                context.driver_name = new_driver_name
                            if new_load_number and new_load_number != context.load_number:
                                context.load_number = new_load_number

                if response:
                    await websocket.send_text(json.dumps(response))
                    if response.get('response_id') == 0:
                        opening_sent = True

                # Check if we should end the call
                if response and response.get("end_call", False):
                    break

        except WebSocketDisconnect:
            pass
        except Exception as e:
            logger.error(f"WebSocket error: {e}", exc_info=True)
        finally:
            # Save call data and cleanup context when call ends
            if not call_id:
                active_contexts = self.context_manager.get_all_active_contexts()
                if active_contexts:
                    call_id = active_contexts[0]
            
            if call_id:
                await self._save_call_data(call_id)
                self.context_manager.remove_context(call_id)

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
        """
        try:
            retell_call_id = message.get("call_id")
            variables = message.get("retell_llm_dynamic_variables", {})

            # Extract call info - prioritize dynamic variables from Retell
            internal_call_id = variables.get("call_id", retell_call_id)
            driver_name = variables.get("driver_name")
            load_number = variables.get("load_number")
            phone_number = variables.get("phone_number", "Unknown")
            scenario = variables.get("scenario", "check_in")
            
            # Handle empty values
            if not driver_name or driver_name.strip() == "":
                driver_name = None
            if not load_number or load_number.strip() == "":
                load_number = None

            # Get agent_config_id if available
            agent_config_id = variables.get("agent_config_id")
            if not agent_config_id and internal_call_id and internal_call_id != retell_call_id:
                try:
                    supabase = get_supabase()
                    call_result = supabase.table("calls").select("agent_config_id").eq("id", internal_call_id).execute()
                    if call_result.data:
                        agent_config_id = call_result.data[0].get("agent_config_id")
                except Exception:
                    pass

            # Get expected route for location conflict detection
            from app.services.llm.realtime import get_route_for_load
            expected_route = get_route_for_load(load_number)

            # Check if context already exists (might have been created proactively from database)
            existing_context = self.context_manager.get_context(internal_call_id)
            if existing_context:
                # Update context with values from dynamic variables (they override database values)
                if driver_name:
                    existing_context.driver_name = driver_name
                if load_number:
                    existing_context.load_number = load_number
                if phone_number and phone_number != "Unknown":
                    existing_context.phone_number = phone_number
                if scenario:
                    existing_context.scenario = scenario
                if retell_call_id:
                    existing_context.retell_call_id = retell_call_id
                if agent_config_id:
                    existing_context.agent_config_id = agent_config_id
                existing_context.expected_route = expected_route
                context = existing_context
            else:
                # Create new conversation context with values from dynamic variables
                context = self.context_manager.create_context(
                    call_id=internal_call_id,
                    scenario=scenario,
                    driver_name=driver_name,
                    load_number=load_number,
                    phone_number=phone_number,
                    expected_route=expected_route,
                    retell_call_id=retell_call_id,
                    agent_config_id=agent_config_id
                )

            # Generate opening greeting using context values
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
        except Exception as e:
            logger.error(f"Error in _handle_call_details: {e}", exc_info=True)
            return {
                "response_type": "response",
                "response_id": 0,
                "content": "I'm having technical difficulties. Let me have a dispatcher call you back.",
                "content_complete": True,
                "end_call": True
            }

    def _generate_opening(self, context) -> str:
        """Generate opening greeting based on scenario"""
        if context.scenario == "emergency":
            if context.driver_name:
                return f"This is Dispatch calling about an emergency. {context.driver_name}, are you able to talk?"
            else:
                return "This is Dispatch calling about an emergency. Are you able to talk?"
        else:
            # Handle missing driver_name or load_number for test calls
            if context.driver_name and context.load_number:
                return f"Hi {context.driver_name}, this is Dispatch with a check call on load {context.load_number}. Can you give me an update on your status?"
            elif context.driver_name:
                return f"Hi {context.driver_name}, this is Dispatch with a check call. Can you tell me which load you're working on and give me an update on your status?"
            elif context.load_number:
                return f"Hi, this is Dispatch with a check call on load {context.load_number}. Can you tell me your name and give me an update on your status?"
            else:
                # For Retell UI test calls without any info
                return "Hi, this is Dispatch with a check call. Can you tell me your name and which load you're working on?"

    async def _create_context_from_retell_id(self, retell_call_id: str) -> str:
        """
        Create conversation context by looking up the last created call with "initiated" status
        
        Args:
            retell_call_id: The Retell call ID from the URL path (used for updating the call)
        
        Returns:
            Internal call ID if context was created, None otherwise
        """
        try:
            supabase = get_supabase()

            # Always get the last created call with "initiated" status
            result = supabase.table("calls").select(
                "id, driver_name, driver_phone, load_number, agent_config_id, agent_configs(scenario_type)"
            ).eq("status", "initiated").order("created_at", desc=True).limit(1).execute()

            if not result.data or len(result.data) == 0:
                logger.error(f"No initiated call found")
                return None

            call_data = result.data[0]
            internal_call_id = call_data["id"]
            driver_name = call_data.get("driver_name")
            load_number = call_data.get("load_number")
            phone_number = call_data.get("driver_phone", "Unknown")
            agent_config_id = call_data.get("agent_config_id")

            # Get scenario from agent_config
            agent_config = call_data.get("agent_configs")
            scenario = agent_config.get("scenario_type", "check_in") if agent_config else "check_in"

            # Update this call with the retell_call_id and set status to in_progress
            supabase.table("calls").update({
                "retell_call_id": retell_call_id,
                "status": "in_progress"
            }).eq("id", internal_call_id).execute()

            # Create call_started event (only if not already created by webhook)
            try:
                from app.services.call_service import CallService
                from app.models.call import CallEventCreate
                call_service = CallService(supabase)
                # Check if call_started event already exists
                existing_events = await call_service.get_call_events(internal_call_id)
                has_started_event = any(e.get("event_type") == "call_started" for e in existing_events)
                
                if not has_started_event:
                    await call_service.create_call_event(
                        CallEventCreate(
                            call_id=internal_call_id,
                            event_type="call_started",
                            event_data={
                                "retell_call_id": retell_call_id,
                                "triggered_by": "websocket_connection"
                            }
                        )
                    )
            except Exception as e:
                logger.error(f"Error creating call_started event: {e}")

            # Get expected route for location conflict detection
            from app.services.llm.realtime import get_route_for_load
            expected_route = get_route_for_load(load_number)

            # Create conversation context
            context = self.context_manager.create_context(
                call_id=internal_call_id,
                scenario=scenario,
                driver_name=driver_name,
                load_number=load_number,
                phone_number=phone_number,
                expected_route=expected_route,
                retell_call_id=retell_call_id,
                agent_config_id=agent_config_id
            )

            return internal_call_id

        except Exception as e:
            logger.error(f"Error creating context from retell_call_id: {e}", exc_info=True)
            return None

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

        # Check if we have an active context
        active_contexts = self.context_manager.get_all_active_contexts()
        
        if not active_contexts:
            return self._error_response(response_id)

        if not transcript:
            return self._error_response(response_id)

        # Get last user utterance
        last_user_turn = None
        for turn in reversed(transcript):
            if turn.get("role") == "user":
                last_user_turn = turn
                break

        if not last_user_turn:
            return self._error_response(response_id)

        user_utterance = last_user_turn.get("content", "")

        call_id = active_contexts[0]
        context = self.context_manager.get_context(call_id)

        if not context:
            return self._error_response(response_id)

        # Generate response using realtime handler
        agent_response, should_end = await self.realtime_handler.generate_response(
            context=context,
            user_utterance=user_utterance,
            confidence=None
        )

        # If should end and not already handled in generate_response
        if should_end and not context.is_emergency:
            final_response = self.realtime_handler.generate_final_response(context)
            agent_response = final_response
        elif should_end and context.is_emergency:
            # Emergency escalation message already set in generate_response
            pass

        # Log emergency detection for call events
        if context.is_emergency and not hasattr(context, '_emergency_event_logged'):
            try:
                from app.database import get_supabase
                from app.services.call_service import CallService
                from app.models.call import CallEventCreate
                supabase = get_supabase()
                call_service = CallService(supabase)
                await call_service.create_call_event(
                    CallEventCreate(
                        call_id=context.call_id,
                        event_type="emergency_detected",
                        event_data={"triggered_at_turn": context.emergency_triggered_at}
                    )
                )
                context._emergency_event_logged = True
            except Exception as e:
                logger.error(f"Error creating emergency event: {e}")

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

        This can be used to prompt the user if they haven't spoken in a while.
        However, if the conversation is already complete (all required data gathered),
        we should end the call instead of asking "are you still there?"
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

        # Check if conversation should end (all required data gathered)
        should_end = self.realtime_handler._should_end_conversation(context)
        
        if should_end:
            # Conversation is complete, end the call with a final message
            context.mark_for_end("conversation_complete")
            final_response = self.realtime_handler.generate_final_response(context)
            context.add_turn(TurnRole.AGENT, final_response)
            
            return {
                "response_type": "response",
                "response_id": response_id,
                "content": final_response,
                "content_complete": True,
                "end_call": True
            }

        # Conversation is not complete, ask if they're still there
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

    async def _save_call_data(self, call_id: str):
        """
        Save extracted conversation data to database when call ends
        
        Updates the call record with final transcript, structured data, and success status.
        
        Args:
            call_id: Internal call ID
        """
        try:
            # Import dependencies
            from app.database import get_supabase
            from app.services.call_service import CallService
            from app.models.call import CallUpdate, CallStatus
            from datetime import datetime, timedelta

            # Get context before it's removed
            context = self.context_manager.get_context(call_id)
            if not context:
                logger.warning(f"No context found for call {call_id}, cannot save data")
                return

            # Build transcript from conversation history
            transcript_lines = []
            for turn in context.conversation_history:
                role = "Dispatcher" if turn.role == TurnRole.AGENT else "Driver"
                transcript_lines.append(f"{role}: {turn.content}")
            transcript = "\n\n".join(transcript_lines)

            # Get extracted data and determine success
            structured_data = context.extracted_data.copy()  # Make a copy to avoid modifying context
            
            # For emergency calls, ensure all required fields are present and properly formatted
            if context.is_emergency:
                # Ensure call_outcome is set
                if "call_outcome" not in structured_data or structured_data["call_outcome"] != "Emergency Escalation":
                    structured_data["call_outcome"] = "Emergency Escalation"
                
                # Ensure escalation_status is set
                if "escalation_status" not in structured_data:
                    structured_data["escalation_status"] = "Connected to Human Dispatcher"
                
                # Extract final structured data from full transcript using emergency schema
                from app.services.llm.extractor import get_extractor
                extractor = get_extractor()
                try:
                    final_extracted = await extractor.extract_from_transcript(
                        transcript=transcript,
                        scenario_type="emergency",
                        driver_name=context.driver_name,
                        load_number=context.load_number
                    )
                    # Merge final extraction with incremental data (final takes precedence)
                    structured_data.update(final_extracted)
                except Exception as e:
                    logger.error(f"Error in final emergency extraction: {e}")
                
                call_outcome = structured_data.get("call_outcome", "Emergency Escalation")
                status = CallStatus.ESCALATED
            else:
                # For non-emergency calls, extract final structured data
                from app.services.llm.extractor import get_extractor
                extractor = get_extractor()
                try:
                    final_extracted = await extractor.extract_from_transcript(
                        transcript=transcript,
                        scenario_type=context.scenario,
                        driver_name=context.driver_name,
                        load_number=context.load_number
                    )
                    # Merge final extraction with incremental data
                    structured_data.update(final_extracted)
                except Exception as e:
                    logger.error(f"Error in final extraction: {e}")
                
                call_outcome = structured_data.get("call_outcome", "Completed")
                
                # Determine if call was successful based on extracted data
                # Check if all required fields are present
                required_fields = ["call_outcome", "driver_status"]
                has_required_data = all(field in structured_data and structured_data[field] for field in required_fields)
                
                # Determine final status
                if context.end_call_reason in ["unresponsive_driver", "poor_connection"]:
                    status = CallStatus.FAILED
                elif has_required_data and call_outcome in ["Completed", "Successful", "In-Transit Update", "Arrival Confirmation"]:
                    status = CallStatus.COMPLETED
                elif transcript:
                    status = CallStatus.COMPLETED  # If we have transcript, consider it completed
                else:
                    status = CallStatus.FAILED

            # Calculate call duration (rough estimate from turn count)
            call_duration = len(context.conversation_history) * 5  # Rough estimate: 5 seconds per turn

            # Get services
            supabase = get_supabase()
            call_service = CallService(supabase)
            from app.models.call import CallEventCreate

            # Update existing call record
            existing_call = await call_service.get_call(call_id)
            
            if existing_call:
                await call_service.update_call(
                    call_id=call_id,
                    call_update=CallUpdate(
                        status=status,
                        raw_transcript=transcript,
                        structured_data=structured_data,
                        call_outcome=call_outcome,
                        call_duration_seconds=call_duration,
                        retell_call_id=context.retell_call_id,
                        completed_at=datetime.now()
                    )
                )
                
                # Create call_completed event
                try:
                    await call_service.create_call_event(
                        CallEventCreate(
                            call_id=call_id,
                            event_type="call_completed",
                            event_data={
                                "status": status.value if hasattr(status, 'value') else str(status),
                                "call_outcome": call_outcome,
                                "duration_seconds": call_duration,
                                "is_emergency": context.is_emergency,
                                "end_call_reason": context.end_call_reason
                            }
                        )
                    )
                except Exception as e:
                    logger.error(f"Error creating call_completed event: {e}")
            else:
                logger.error(f"Call record {call_id} not found, cannot update")

        except Exception as e:
            logger.error(f"Error saving call data for {call_id}: {e}", exc_info=True)

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
    WebSocket endpoint for Retell AI Custom LLM (base path)

    Retell will connect to: ws://your-domain/ws/llm

    This endpoint handles real-time conversation during calls
    """
    await _ws_handler.handle_connection(websocket)


@router.websocket("/llm/{call_id:path}")
async def retell_llm_websocket_with_call_id(websocket: WebSocket, call_id: str):
    """
    WebSocket endpoint for Retell AI Custom LLM with call ID in path

    Retell appends the call ID to the WebSocket URL in formats like:
    - ws://your-domain/ws/llm/call_d458af3989b089f096ea90269d3
    - wss://your-ngrok-url/ws/llm/call_abc123

    This endpoint accepts those formats while maintaining compatibility
    with the base /ws/llm endpoint.

    Args:
        websocket: FastAPI WebSocket connection
        call_id: Retell call ID from URL path - used to look up our internal call
    """
    logger.info(f"WebSocket connection attempt with call_id in path: {call_id}")
    await _ws_handler.handle_connection(websocket, retell_call_id=call_id)
