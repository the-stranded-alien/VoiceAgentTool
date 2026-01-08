from typing import Dict, Any, List
import logging
from datetime import datetime
from app.services.call_service import CallService
from app.services.llm.extractor import get_extractor
from app.services.llm.conversation import get_conversation_handler
from app.database import get_supabase
from app.models.call import CallUpdate, CallStatus, CallEventCreate

logger = logging.getLogger(__name__)

class RetellWebhookHandler:
    """Handler for Retell AI webhook events (SDK compatible)"""
    
    def __init__(self):
        self.extractor = get_extractor()
        self.conversation = get_conversation_handler()
    
    async def handle_call_started(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle call_started event from Retell
        
        Payload structure from SDK:
        {
            "event": "call_started",
            "call": {
                "call_id": "...",
                "agent_id": "...",
                "metadata": {...}
            }
        }
        """
        try:
            call_data = payload.get("call", {})
            retell_call_id = call_data.get("call_id")
            metadata = call_data.get("metadata", {})
            internal_call_id = metadata.get("internal_call_id")
            
            logger.info(f"Call started: {retell_call_id}")
            
            if internal_call_id:
                supabase = get_supabase()
                call_service = CallService(supabase)
                
                await call_service.update_call(
                    call_id=internal_call_id,
                    call_update=CallUpdate(
                        status=CallStatus.IN_PROGRESS,
                        started_at=datetime.now()
                    )
                )
                
                await call_service.create_call_event(
                    CallEventCreate(
                        call_id=internal_call_id,
                        event_type="call_started",
                        event_data=payload
                    )
                )
            
            return {"status": "success"}
            
        except Exception as e:
            logger.error(f"Error handling call_started: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def handle_call_ended(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle call_ended event from Retell
        
        Payload structure:
        {
            "event": "call_ended",
            "call": {
                "call_id": "...",
                "agent_id": "...",
                "call_status": "ended",
                "transcript": "...",
                "transcript_object": [...],
                "recording_url": "...",
                "call_analysis": {...},
                "metadata": {...}
            }
        }
        """
        try:
            call_data = payload.get("call", {})
            retell_call_id = call_data.get("call_id")
            metadata = call_data.get("metadata", {})
            internal_call_id = metadata.get("internal_call_id")
            
            # Extract transcript
            transcript = call_data.get("transcript", "")
            transcript_object = call_data.get("transcript_object", [])
            
            # Extract call analysis
            call_analysis = call_data.get("call_analysis", {})
            call_duration = call_analysis.get("call_duration_seconds", 0)
            
            logger.info(f"Call ended: {retell_call_id}, duration: {call_duration}s")
            
            if internal_call_id:
                supabase = get_supabase()
                call_service = CallService(supabase)
                
                # Get call to determine scenario
                call = await call_service.get_call(internal_call_id)
                if not call:
                    logger.error(f"Call {internal_call_id} not found")
                    return {"status": "error", "message": "Call not found"}
                
                # Get agent config
                from app.services.agent_service import AgentService
                agent_service = AgentService(supabase)
                agent = await agent_service.get_agent(call.agent_config_id)
                
                scenario_type = agent.scenario_type if agent else "check_in"
                
                # Extract structured data
                structured_data = {}
                if transcript:
                    structured_data = await self.extractor.extract_from_transcript(
                        transcript=transcript,
                        scenario_type=scenario_type,
                        driver_name=call.driver_name,
                        load_number=call.load_number
                    )
                
                call_outcome = structured_data.get("call_outcome", "Completed")
                
                # Determine final status
                if call_outcome == "Emergency Escalation":
                    status = CallStatus.ESCALATED
                elif transcript:
                    status = CallStatus.COMPLETED
                else:
                    status = CallStatus.FAILED
                
                # Update call
                await call_service.update_call(
                    call_id=internal_call_id,
                    call_update=CallUpdate(
                        status=status,
                        raw_transcript=transcript,
                        structured_data=structured_data,
                        call_outcome=call_outcome,
                        call_duration_seconds=call_duration,
                        completed_at=datetime.now()
                    )
                )
                
                # Log event
                await call_service.create_call_event(
                    CallEventCreate(
                        call_id=internal_call_id,
                        event_type="call_ended",
                        event_data={
                            "retell_call_id": retell_call_id,
                            "call_analysis": call_analysis,
                            "recording_url": call_data.get("recording_url")
                        }
                    )
                )
                
                logger.info(f"Processed call {internal_call_id}: {call_outcome}")
            
            return {"status": "success"}
            
        except Exception as e:
            logger.error(f"Error handling call_ended: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def handle_call_analyzed(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle call_analyzed event (fired after AI analysis)
        
        Contains additional insights like sentiment, call success, etc.
        """
        try:
            call_data = payload.get("call", {})
            call_analysis = call_data.get("call_analysis", {})
            
            # Extract useful metrics
            user_sentiment = call_analysis.get("user_sentiment")
            call_successful = call_analysis.get("call_successful")
            
            logger.info(f"Call analyzed - Sentiment: {user_sentiment}, Success: {call_successful}")
            
            # You can store additional analysis in database if needed
            
            return {"status": "success"}
            
        except Exception as e:
            logger.error(f"Error handling call_analyzed: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _format_transcript_object(self, transcript_obj: List[Dict[str, Any]]) -> str:
        """
        Format transcript_object into readable text
        
        Args:
            transcript_obj: List of conversation turns
            
        Returns:
            Formatted transcript string
        """
        formatted = []
        for turn in transcript_obj:
            role = turn.get("role", "")
            content = turn.get("content", "")
            
            if role == "agent":
                formatted.append(f"Dispatcher: {content}")
            elif role == "user":
                formatted.append(f"Driver: {content}")
        
        return "\n\n".join(formatted)


# Singleton
_webhook_handler = None

def get_webhook_handler() -> RetellWebhookHandler:
    """Get or create webhook handler singleton"""
    global _webhook_handler
    if _webhook_handler is None:
        _webhook_handler = RetellWebhookHandler()
    return _webhook_handler