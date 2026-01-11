from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
import logging
from app.database import get_supabase
from app.services.llm.extractor import get_extractor
from app.services.retell.call import get_retell_call_service
from app.services.retell.agent import get_retell_agent_service
from app.services.agent_service import AgentService
from app.services.call_service import CallService
from app.models.call import (
    CallCreate,
    CallUpdate,
    CallResponse,
    CallStatus,
    CallEventCreate,
    TodayStatsResponse
)
from app.models.agent import AgentConfigUpdate
from supabase import Client

logger = logging.getLogger(__name__)

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
    
@router.post("/{call_id}/initiate")
async def initiate_call(
    call_id: str,
    use_web_call: bool = False,
    call_service: CallService = Depends(get_call_service)
):
    """
    Initiate a call via Retell AI (using SDK)
    
    Args:
        call_id: Internal call ID
        use_web_call: True for web call (browser testing), False for phone call
    """
    try:
        # Get call details
        call = await call_service.get_call(call_id)
        if not call:
            raise HTTPException(status_code=404, detail="Call not found")
        
        # Get agent configuration
        supabase = get_supabase()
        agent_service = AgentService(supabase)
        agent = await agent_service.get_agent(call.agent_config_id)
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Ensure agent has Retell agent ID (fallback for agents created before immediate creation was implemented)
        retell_agent_id = agent.retell_agent_id
        if not retell_agent_id:
            # Create Retell agent as fallback (should rarely happen now)
            logger.warning(f"Agent {agent.name} missing retell_agent_id, creating now (fallback)")
            retell_agent_service = get_retell_agent_service()
            retell_agent_id = retell_agent_service.create_agent_from_config(
                agent_config=agent.dict()
            )
            
            # Update our agent with Retell ID
            await agent_service.update_agent(
                agent_id=call.agent_config_id,
                agent_update=AgentConfigUpdate(retell_agent_id=retell_agent_id)
            )
        
        # Initiate call
        retell_call_service = get_retell_call_service()
        
        if use_web_call:
            # Web call for browser testing
            result = await retell_call_service.create_web_call(
                call_id=call_id,
                retell_agent_id=retell_agent_id,
                driver_name=call.driver_name,
                load_number=call.load_number,
                scenario=agent.scenario_type
            )
            
            return {
                "success": True,
                "type": "web_call",
                "call_id": call_id,
                "retell_call_id": result["retell_call_id"],
                "access_token": result["access_token"],
                "sample_rate": result["sample_rate"],
                "message": "Web call created. Use this with Retell Web SDK."
            }
        else:
            # Phone call
            result = await retell_call_service.initiate_phone_call(
                call_id=call_id,
                retell_agent_id=retell_agent_id,
                driver_phone=call.driver_phone,
                driver_name=call.driver_name,
                load_number=call.load_number,
                scenario=agent.scenario_type
            )
            
            return {
                "success": True,
                "type": "phone_call",
                "call_id": call_id,
                "retell_call_id": result["retell_call_id"],
                "from_number": result["from_number"],
                "to_number": result["to_number"],
                "message": "Phone call initiated successfully"
            }
        
    except Exception as e:
        logger.error(f"Failed to initiate call: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))