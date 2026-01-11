from typing import Dict, Any, Optional
import logging
from datetime import datetime
from app.services.retell.client import get_retell_client
from app.services.call_service import CallService
from app.database import get_supabase
from app.models.call import CallUpdate, CallStatus

logger = logging.getLogger(__name__)

class RetellCallService:
    """Service for managing Retell AI calls using SDK"""
    
    def __init__(self):
        self.client = get_retell_client()
    
    async def initiate_phone_call(
        self,
        call_id: str,
        retell_agent_id: str,
        driver_phone: str,
        driver_name: str,
        load_number: str,
        scenario: str = "check_in",
        from_number: Optional[str] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Initiate a phone call through Retell AI
        
        Args:
            call_id: Our internal call ID
            retell_agent_id: Retell agent ID to use
            driver_phone: Driver's phone number
            driver_name: Driver's name (for LLM context)
            load_number: Load number (for LLM context)
            from_number: Retell phone number (optional, auto-selected if None)
            additional_metadata: Extra metadata to pass
            
        Returns:
            Dict with call details including retell_call_id
        """
        try:
            # Get available phone numbers if not provided
            if not from_number:
                phone_numbers = self.client.list_phone_numbers()
                if not phone_numbers:
                    raise ValueError("No phone numbers available in Retell account. Please purchase a number.")
                from_number = phone_numbers[0].phone_number
            
            # Prepare metadata
            metadata = {
                "internal_call_id": call_id,
                "driver_name": driver_name,
                "load_number": load_number,
            }
            if additional_metadata:
                metadata.update(additional_metadata)
            
            # Prepare dynamic variables for LLM prompt customization
            # These are passed to the WebSocket handler via Retell
            dynamic_variables = {
                "call_id": call_id,
                "driver_name": driver_name,
                "load_number": load_number,
                "scenario": scenario,
                "phone_number": driver_phone,
            }

            # Create phone call using SDK
            response = self.client.create_phone_call(
                from_number=from_number,
                to_number=driver_phone,
                agent_id=retell_agent_id,
                metadata=metadata,
                retell_llm_dynamic_variables=dynamic_variables
            )
            
            # Update our database
            supabase = get_supabase()
            call_service = CallService(supabase)
            await call_service.update_call(
                call_id=call_id,
                call_update=CallUpdate(
                    retell_call_id=response.call_id,
                    status=CallStatus.IN_PROGRESS,
                    started_at=datetime.now()
                )
            )
            
            logger.info(f"Initiated phone call {call_id} -> Retell {response.call_id}")
            
            return {
                "call_id": call_id,
                "retell_call_id": response.call_id,
                "from_number": from_number,
                "to_number": driver_phone,
                "agent_id": retell_agent_id
            }
            
        except Exception as e:
            logger.error(f"Failed to initiate phone call: {str(e)}")
            
            # Update call status to failed
            supabase = get_supabase()
            call_service = CallService(supabase)
            await call_service.update_call(
                call_id=call_id,
                call_update=CallUpdate(
                    status=CallStatus.FAILED,
                    error_message=str(e)
                )
            )
            raise
    
    async def create_web_call(
        self,
        call_id: str,
        retell_agent_id: str,
        driver_name: str,
        load_number: str,
        scenario: str = "check_in",
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a web call for browser-based testing
        
        Args:
            call_id: Our internal call ID
            retell_agent_id: Retell agent ID
            driver_name: Driver's name
            load_number: Load number
            additional_metadata: Extra metadata
            
        Returns:
            Dict with call_id, retell_call_id, and access_token
        """
        try:
            # Prepare metadata
            metadata = {
                "internal_call_id": call_id,
                "driver_name": driver_name,
                "load_number": load_number,
            }
            if additional_metadata:
                metadata.update(additional_metadata)
            
            # Dynamic variables for LLM
            # These are passed to the WebSocket handler via Retell
            dynamic_variables = {
                "call_id": call_id,
                "driver_name": driver_name,
                "load_number": load_number,
                "scenario": scenario,
            }

            # Create web call using SDK
            response = self.client.create_web_call(
                agent_id=retell_agent_id,
                metadata=metadata,
                retell_llm_dynamic_variables=dynamic_variables
            )

            logger.info(f"Retell web call created: {response.call_id}, updating database...")
            logger.info(f"Web call created: {response.call_id}, updating database for call_id: {call_id}")

            # Update database BEFORE returning - this is critical for WebSocket lookup
            supabase = get_supabase()
            call_service = CallService(supabase)
            update_result = await call_service.update_call(
                call_id=call_id,
                call_update=CallUpdate(
                    retell_call_id=response.call_id,
                    status=CallStatus.IN_PROGRESS,
                    started_at=datetime.now()
                )
            )

            if update_result:
                logger.info(f"Database updated successfully for call {call_id} with retell_call_id {response.call_id}")
                logger.info(f"Database updated: retell_call_id={response.call_id} saved for call_id={call_id}")
            else:
                logger.error(f"Failed to update database for call {call_id}")
                logger.warning(f"Database update returned None for call_id={call_id}")

            return {
                "call_id": call_id,
                "retell_call_id": response.call_id,
                "access_token": response.access_token,
                "agent_id": retell_agent_id,
                "sample_rate": getattr(response, 'sample_rate', 24000)
            }
            
        except Exception as e:
            logger.error(f"Failed to create web call: {str(e)}")
            
            # Update call status
            supabase = get_supabase()
            call_service = CallService(supabase)
            await call_service.update_call(
                call_id=call_id,
                call_update=CallUpdate(
                    status=CallStatus.FAILED,
                    error_message=str(e)
                )
            )
            raise
    
    async def get_call_details(self, retell_call_id: str) -> Dict[str, Any]:
        """
        Get call details from Retell
        
        Args:
            retell_call_id: Retell call ID
            
        Returns:
            Call details dict
        """
        try:
            call = self.client.get_call(retell_call_id)
            
            # Convert SDK response to dict
            return {
                "call_id": call.call_id,
                "agent_id": call.agent_id,
                "call_status": call.call_status,
                "start_timestamp": call.start_timestamp,
                "end_timestamp": call.end_timestamp,
                "transcript": call.transcript if hasattr(call, 'transcript') else None,
                "metadata": call.metadata if hasattr(call, 'metadata') else {}
            }
        except Exception as e:
            logger.error(f"Failed to get call details: {str(e)}")
            raise
    
    async def list_calls(
        self,
        agent_id: Optional[str] = None,
        limit: int = 100
    ):
        """List calls with optional filtering"""
        try:
            filter_criteria = {}
            if agent_id:
                filter_criteria["agent_id"] = agent_id
            
            return self.client.list_calls(
                filter_criteria=filter_criteria if filter_criteria else None,
                limit=limit
            )
        except Exception as e:
            logger.error(f"Failed to list calls: {str(e)}")
            raise


# Singleton
_call_service = None

def get_retell_call_service() -> RetellCallService:
    """Get or create call service singleton"""
    global _call_service
    if _call_service is None:
        _call_service = RetellCallService()
    return _call_service