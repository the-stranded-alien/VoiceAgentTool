from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.database import get_supabase
from app.services.llm.extractor import get_extractor
from app.services.call_service import CallService
from app.models.call import (
    CallCreate,
    CallUpdate,
    CallResponse,
    CallStatus,
    CallEventCreate,
    TodayStatsResponse
)
from supabase import Client

router = APIRouter()

def get_call_service(supabase: Client = Depends(get_supabase)) -> CallService:
    return CallService(supabase)

@router.post("/", response_model=CallResponse, status_code=201)
async def create_call(
    call: CallCreate,
    service: CallService = Depends(get_call_service)
):
    """Create a new call"""
    return await service.create_call(call)

@router.get("/", response_model=List[CallResponse])
async def list_calls(
    status: Optional[CallStatus] = None,
    agent_config_id: Optional[str] = None,
    limit: int = 50,
    service: CallService = Depends(get_call_service)
):
    """List calls with optional filters"""
    return await service.list_calls(
        status=status,
        agent_config_id=agent_config_id,
        limit=limit
    )

@router.get("/stats/today", response_model=TodayStatsResponse)
async def get_today_stats(
    service: CallService = Depends(get_call_service)
):
    """Get today's call statistics"""
    return await service.get_today_stats()

@router.get("/{call_id}", response_model=CallResponse)
async def get_call(
    call_id: str,
    service: CallService = Depends(get_call_service)
):
    """Get a specific call"""
    call = await service.get_call(call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    return call

@router.put("/{call_id}", response_model=CallResponse)
async def update_call(
    call_id: str,
    call_update: CallUpdate,
    service: CallService = Depends(get_call_service)
):
    """Update a call"""
    call = await service.update_call(call_id, call_update)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    return call

@router.get("/{call_id}/events")
async def get_call_events(
    call_id: str,
    service: CallService = Depends(get_call_service)
):
    """Get all events for a call"""
    return await service.get_call_events(call_id)

@router.post("/{call_id}/events", status_code=201)
async def create_call_event(
    call_id: str,
    event_type: str,
    event_data: dict = {},
    service: CallService = Depends(get_call_service)
):
    """Create a call event"""
    event = CallEventCreate(
        call_id=call_id,
        event_type=event_type,
        event_data=event_data
    )
    return await service.create_call_event(event)

@router.post("/{call_id}/process-transcript")
async def process_call_transcript(
    call_id: str,
    transcript: str,
    scenario_type: str = "check_in",
    service: CallService = Depends(get_call_service)
):
    """
    Process a call transcript and extract structured data
    
    This endpoint is useful for testing or post-call processing
    """
    try:
        result = await service.process_call_transcript(
            call_id=call_id,
            transcript=transcript,
            scenario_type=scenario_type
        )
        return {
            "success": True,
            "structured_data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))