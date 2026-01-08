from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.database import get_supabase
from app.services.agent_service import AgentService
from app.models.agent import (
    AgentConfigCreate,
    AgentConfigUpdate,
    AgentConfigResponse,
    AgentStatus
)
from supabase import Client

router = APIRouter()

def get_agent_service(supabase: Client = Depends(get_supabase)) -> AgentService:
    return AgentService(supabase)

@router.post("/", response_model=AgentConfigResponse, status_code=201)
async def create_agent(
    agent: AgentConfigCreate,
    service: AgentService = Depends(get_agent_service)
):
    """Create a new agent configuration"""
    return await service.create_agent(agent)

@router.get("/", response_model=List[AgentConfigResponse])
async def list_agents(
    status: Optional[AgentStatus] = None,
    scenario_type: Optional[str] = None,
    service: AgentService = Depends(get_agent_service)
):
    """List all agent configurations"""
    return await service.list_agents(status=status, scenario_type=scenario_type)

@router.get("/{agent_id}", response_model=AgentConfigResponse)
async def get_agent(
    agent_id: str,
    service: AgentService = Depends(get_agent_service)
):
    """Get a specific agent configuration"""
    agent = await service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.put("/{agent_id}", response_model=AgentConfigResponse)
async def update_agent(
    agent_id: str,
    agent_update: AgentConfigUpdate,
    service: AgentService = Depends(get_agent_service)
):
    """Update an agent configuration"""
    agent = await service.update_agent(agent_id, agent_update)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.delete("/{agent_id}", status_code=204)
async def delete_agent(
    agent_id: str,
    service: AgentService = Depends(get_agent_service)
):
    """Delete an agent configuration"""
    success = await service.delete_agent(agent_id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")

@router.get("/performance/metrics")
async def get_agent_performance(
    service: AgentService = Depends(get_agent_service)
):
    """Get performance metrics for all agents"""
    return await service.get_agent_performance()