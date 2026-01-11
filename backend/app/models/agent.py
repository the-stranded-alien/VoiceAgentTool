from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ScenarioType(str, Enum):
    CHECK_IN = "check_in"
    EMERGENCY = "emergency"
    DELIVERY = "delivery"
    CUSTOM = "custom"

class AgentStatus(str, Enum):
    ACTIVE = "active"
    DRAFT = "draft"
    INACTIVE = "inactive"

class VoiceSettings(BaseModel):
    voice_id: str = "default"
    response_delay: float = 0.8
    interruption_sensitivity: float = 0.7
    backchannel: Dict[str, Any] = {"enabled": True, "frequency": "medium"}
    filler_words: Dict[str, Any] = {"enabled": True}
    ambient_sound: bool = False
    speaking_rate: str = "normal"

class AdvancedSettings(BaseModel):
    max_call_duration_minutes: int = 10
    retry_attempts: int = 3
    auto_escalate_emergency: bool = True
    record_calls: bool = True

class AgentConfigBase(BaseModel):
    name: str
    description: Optional[str] = None
    scenario_type: ScenarioType
    system_prompt: str
    conversation_rules: Dict[str, Any] = {}
    voice_settings: VoiceSettings = VoiceSettings()
    advanced_settings: AdvancedSettings = AdvancedSettings()

class AgentConfigCreate(AgentConfigBase):
    status: AgentStatus = AgentStatus.ACTIVE

class AgentConfigUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    scenario_type: Optional[ScenarioType] = None
    system_prompt: Optional[str] = None
    conversation_rules: Optional[Dict[str, Any]] = None
    voice_settings: Optional[VoiceSettings] = None
    advanced_settings: Optional[AdvancedSettings] = None
    status: Optional[AgentStatus] = None
    retell_agent_id: Optional[str] = None

class AgentConfigResponse(AgentConfigBase):
    id: str
    status: AgentStatus
    retell_agent_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True