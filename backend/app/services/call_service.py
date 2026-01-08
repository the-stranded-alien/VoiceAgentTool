from typing import List, Optional
from datetime import datetime
from supabase import Client
from app.models.call import (
    CallCreate,
    CallUpdate,
    CallResponse,
    CallStatus,
    CallEventCreate,
    TodayStatsResponse
)

class CallService:
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.table = "calls"
        self.events_table = "call_events"
    
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
        data = call_update.model_dump(exclude_unset=True)
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
                emergency_calls=stats.get('emergency_calls', 0),
                in_progress_calls=stats.get('in_progress_calls', 0),
                avg_duration_minutes=float(stats.get('avg_duration_minutes', 0.0) or 0.0)
            )
        return TodayStatsResponse(
            total_calls=0,
            successful_calls=0,
            emergency_calls=0,
            in_progress_calls=0,
            avg_duration_minutes=0.0
        )