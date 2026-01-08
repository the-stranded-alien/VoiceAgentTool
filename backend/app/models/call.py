from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class CallStatus(str, Enum):
    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ESCALATED = "escalated"

class CallCreate(BaseModel):
    agent_config_id: str
    driver_name: str
    driver_phone: str
    load_number: str

class CallUpdate(BaseModel):
    status: Optional[CallStatus] = None
    call_outcome: Optional[str] = None
    raw_transcript: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = None
    call_duration_seconds: Optional[int] = None
    error_message: Optional[str] = None
    retell_call_id: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class CallResponse(BaseModel):
    id: str
    agent_config_id: Optional[str]
    driver_name: str
    driver_phone: str
    load_number: str
    retell_call_id: Optional[str]
    status: CallStatus
    call_outcome: Optional[str]
    raw_transcript: Optional[str]
    structured_data: Optional[Dict[str, Any]]
    call_duration_seconds: Optional[int]
    error_message: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True

class CallEventCreate(BaseModel):
    call_id: str
    event_type: str
    event_data: Dict[str, Any] = {}

class TodayStatsResponse(BaseModel):
    total_calls: int
    successful_calls: int
    emergency_calls: int
    in_progress_calls: int
    avg_duration_minutes: float