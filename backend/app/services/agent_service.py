from typing import List, Optional
from supabase import Client
from app.models.agent import (
    AgentConfigCreate,
    AgentConfigUpdate,
    AgentConfigResponse,
    AgentStatus
)

class AgentService:
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.table = "agent_configs"

    async def create_agent(self, agent: AgentConfigCreate) -> AgentConfigResponse:
        """Create a new agent configuration"""
        data = agent.model_dump()
        
        # Convert Pydantic models to dicts for nested objects
        if 'voice_settings' in data:
            data['voice_settings'] = agent.voice_settings.model_dump()
        if 'advanced_settings' in data:
            data['advanced_settings'] = agent.advanced_settings.model_dump()
        
        response = self.supabase.table(self.table).insert(data).execute()
        return AgentConfigResponse(**response.data[0])
    
    async def get_agent(self, agent_id: str) -> Optional[AgentConfigResponse]:
        """Get agent configuration by ID"""
        response = self.supabase.table(self.table).select("*").eq("id", agent_id).execute()
        if response.data:
            return AgentConfigResponse(**response.data[0])
        return None
    
    async def list_agents(
        self, 
        status: Optional[AgentStatus] = None,
        scenario_type: Optional[str] = None
    ) -> List[AgentConfigResponse]:
        """List all agent configurations with optional filters"""
        query = self.supabase.table(self.table).select("*")
        
        if status:
            query = query.eq("status", status.value)
        if scenario_type:
            query = query.eq("scenario_type", scenario_type)
        
        response = query.order("created_at", desc=True).execute()
        return [AgentConfigResponse(**item) for item in response.data]
    
    async def update_agent(
        self, 
        agent_id: str, 
        agent_update: AgentConfigUpdate
    ) -> Optional[AgentConfigResponse]:
        """Update an agent configuration"""
        data = agent_update.model_dump(exclude_unset=True)
        
        # Convert Pydantic models to dicts for nested objects
        if 'voice_settings' in data and data['voice_settings']:
            data['voice_settings'] = agent_update.voice_settings.model_dump()
        if 'advanced_settings' in data and data['advanced_settings']:
            data['advanced_settings'] = agent_update.advanced_settings.model_dump()
        
        response = self.supabase.table(self.table).update(data).eq("id", agent_id).execute()
        if response.data:
            return AgentConfigResponse(**response.data[0])
        return None
    
    async def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent configuration"""
        response = self.supabase.table(self.table).delete().eq("id", agent_id).execute()
        return len(response.data) > 0
    
    async def get_agent_performance(self):
        """Get performance metrics for all agents"""
        response = self.supabase.table("agent_performance_metrics").select("*").execute()
        return response.data