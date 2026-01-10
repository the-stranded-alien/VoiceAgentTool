from pydantic import BaseModel, Field, model_validator
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
    driver_phone: Optional[str] = None
    phone_number: Optional[str] = Field(default=None, exclude=True)  # Frontend field, not in DB
    load_number: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def validate_phone(cls, data: Any) -> Any:
        """Accept either driver_phone or phone_number from frontend"""
        if isinstance(data, dict):
            # If phone_number is provided but not driver_phone, copy it
            if data.get('phone_number') and not data.get('driver_phone'):
                data['driver_phone'] = data['phone_number']
            # If driver_phone is provided but not phone_number, copy it
            elif data.get('driver_phone') and not data.get('phone_number'):
                data['phone_number'] = data['driver_phone']

            # Ensure at least one phone field is provided
            if not data.get('driver_phone') and not data.get('phone_number'):
                raise ValueError('Either driver_phone or phone_number must be provided')
        return data

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
    failed_calls: int
    in_progress_calls: int
    avg_duration: Optional[float] = None
    emergency_calls: Optional[int] = None