from typing import Any, List, Optional, Dict
from datetime import datetime
import logging
from supabase import Client
from app.models.call import (
    CallCreate,
    CallUpdate,
    CallResponse,
    CallStatus,
    CallEventCreate,
    TodayStatsResponse
)
from app.services.llm.extractor import get_extractor
from app.services.llm.conversation import get_conversation_handler

logger = logging.getLogger(__name__)

class CallService:
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.table = "calls"
        self.events_table = "call_events"
        self.extractor = get_extractor()
        self.conversation = get_conversation_handler()
    
    async def create_call(self, call: CallCreate) -> CallResponse:
        """Create a new call record"""
        data = call.model_dump()
        response = self.supabase.table(self.table).insert(data).execute()
        return CallResponse(**response.data[0])
    
    async def get_call(self, call_id: str) -> Optional[CallResponse]:
        """Get call by ID"""
        response = self.supabase.table(self.table).select("*").eq("id", call_id).execute()
        if response.data:
            return CallResponse(**response.data[0])
        return None
    
    async def get_call_by_retell_id(self, retell_call_id: str) -> Optional[CallResponse]:
        """Get call by Retell AI call ID"""
        response = self.supabase.table(self.table).select("*").eq("retell_call_id", retell_call_id).execute()
        if response.data:
            return CallResponse(**response.data[0])
        return None
    
    async def list_calls(
        self,
        status: Optional[CallStatus] = None,
        agent_config_id: Optional[str] = None,
        limit: int = 50
    ) -> List[CallResponse]:
        """List calls with optional filters"""
        query = self.supabase.table(self.table).select("*")
        
        if status:
            query = query.eq("status", status.value)
        if agent_config_id:
            query = query.eq("agent_config_id", agent_config_id)
        
        response = query.order("created_at", desc=True).limit(limit).execute()
        return [CallResponse(**item) for item in response.data]
    
    async def update_call(
        self,
        call_id: str,
        call_update: CallUpdate
    ) -> Optional[CallResponse]:
        """Update a call record"""
        data = call_update.model_dump(exclude_unset=True, mode='json')
        response = self.supabase.table(self.table).update(data).eq("id", call_id).execute()
        if response.data:
            return CallResponse(**response.data[0])
        return None
    
    async def create_call_event(self, event: CallEventCreate):
        """Create a call event for debugging"""
        data = event.model_dump()
        response = self.supabase.table(self.events_table).insert(data).execute()
        return response.data[0]
    
    async def get_call_events(self, call_id: str):
        """Get all events for a call"""
        response = self.supabase.table(self.events_table).select("*").eq("call_id", call_id).order("timestamp", desc=False).execute()
        return response.data
    
    async def get_today_stats(self) -> TodayStatsResponse:
        """Get today's call statistics"""
        response = self.supabase.rpc("get_today_stats").execute()
        if response.data:
            stats = response.data[0]
            return TodayStatsResponse(
                total_calls=stats.get('total_calls', 0),
                successful_calls=stats.get('successful_calls', 0),
                failed_calls=stats.get('failed_calls', 0),
                in_progress_calls=stats.get('in_progress_calls', 0),
                avg_duration=float(stats.get('avg_duration_minutes', 0.0) or 0.0) if stats.get('avg_duration_minutes') else None,
                emergency_calls=stats.get('emergency_calls', 0)
            )
        return TodayStatsResponse(
            total_calls=0,
            successful_calls=0,
            failed_calls=0,
            in_progress_calls=0,
            avg_duration=None,
            emergency_calls=0
        )
    
    async def process_call_transcript(
        self,
        call_id: str,
        transcript: str,
        scenario_type: str
    ) -> Dict[str, Any]:
        """
        Process transcript and extract structured data
        
        Args:
            call_id: Call ID
            transcript: Raw transcript
            scenario_type: Type of scenario
            
        Returns:
            Extracted structured data
        """
        try:
            # Get call details
            call = await self.get_call(call_id)
            if not call:
                raise ValueError(f"Call {call_id} not found")
            
            # Extract structured data
            structured_data = await self.extractor.extract_from_transcript(
                transcript=transcript,
                scenario_type=scenario_type,
                driver_name=call.driver_name,
                load_number=call.load_number
            )
            
            # Classify call outcome
            outcome = await self.extractor.classify_call_outcome(transcript)
            
            # Update call with results
            await self.update_call(
                call_id=call_id,
                call_update=CallUpdate(
                    raw_transcript=transcript,
                    structured_data=structured_data,
                    call_outcome=outcome,
                    status=CallStatus.COMPLETED
                )
            )
            
            return structured_data
            
        except Exception as e:
            logger.error(f"Error processing transcript: {str(e)}")
            raise