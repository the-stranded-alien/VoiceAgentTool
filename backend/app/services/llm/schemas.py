from typing import Dict, Any, List
from enum import Enum

class ScenarioType(str, Enum):
    CHECK_IN = "check_in"
    EMERGENCY = "emergency"
    DELIVERY = "delivery"

# Schema definitions for structured data extraction
CHECK_IN_SCHEMA = {
    "call_outcome": {
        "type": "string",
        "enum": ["In-Transit Update", "Arrival Confirmation"],
        "description": "Whether driver is in-transit or has arrived"
    },
    "driver_status": {
        "type": "string",
        "enum": ["Driving", "Delayed", "Arrived", "Unloading"],
        "description": "Current status of the driver"
    },
    "current_location": {
        "type": "string",
        "nullable": True,
        "description": "Driver's current location (e.g., 'I-10 near Indio, CA')"
    },
    "eta": {
        "type": "string",
        "nullable": True,
        "description": "Estimated time of arrival (e.g., 'Tomorrow, 8:00 AM')"
    },
    "delay_reason": {
        "type": "string",
        "enum": ["Heavy Traffic", "Weather", "Mechanical", "None", "Other"],
        "nullable": True,
        "description": "Reason for any delays"
    },
    "unloading_status": {
        "type": "string",
        "nullable": True,
        "description": "Unloading status if arrived (e.g., 'In Door 42', 'Waiting for Lumper')"
    },
    "pod_reminder_acknowledged": {
        "type": "boolean",
        "description": "Whether driver acknowledged POD reminder"
    }
}

EMERGENCY_SCHEMA = {
    "call_outcome": {
        "type": "string",
        "const": "Emergency Escalation",
        "description": "Must always be 'Emergency Escalation'"
    },
    "emergency_type": {
        "type": "string",
        "enum": ["Accident", "Breakdown", "Medical", "Other"],
        "description": "Type of emergency"
    },
    "safety_status": {
        "type": "string",
        "description": "Driver's safety status (e.g., 'Driver confirmed safe')"
    },
    "injury_status": {
        "type": "string",
        "description": "Injury status (e.g., 'No injuries reported', 'Minor injury')"
    },
    "emergency_location": {
        "type": "string",
        "description": "Exact emergency location (e.g., 'I-15 North, Mile Marker 123')"
    },
    "load_secure": {
        "type": "boolean",
        "description": "Whether the load is secure"
    },
    "escalation_status": {
        "type": "string",
        "const": "Connected to Human Dispatcher",
        "description": "Must always be 'Connected to Human Dispatcher'"
    }
}

DELIVERY_SCHEMA = {
    "call_outcome": {
        "type": "string",
        "enum": ["Delivery Confirmed", "Delivery Issues"],
        "description": "Delivery confirmation status"
    },
    "delivery_time": {
        "type": "string",
        "nullable": True,
        "description": "When delivery was completed"
    },
    "pod_received": {
        "type": "boolean",
        "description": "Whether POD was received"
    },
    "pod_number": {
        "type": "string",
        "nullable": True,
        "description": "POD reference number"
    },
    "delivery_issues": {
        "type": "string",
        "nullable": True,
        "description": "Any issues during delivery"
    }
}

# Map scenario types to schemas
SCHEMA_MAP = {
    ScenarioType.CHECK_IN: CHECK_IN_SCHEMA,
    ScenarioType.EMERGENCY: EMERGENCY_SCHEMA,
    ScenarioType.DELIVERY: DELIVERY_SCHEMA
}

def get_schema_for_scenario(scenario_type: str) -> Dict[str, Any]:
    """Get extraction schema for a given scenario type"""
    try:
        scenario = ScenarioType(scenario_type)
        return SCHEMA_MAP[scenario]
    except (ValueError, KeyError):
        # Default to check-in schema
        return CHECK_IN_SCHEMA

def get_schema_description(schema: Dict[str, Any]) -> str:
    """Convert schema to human-readable description for prompt"""
    lines = []
    for field, spec in schema.items():
        field_type = spec.get("type", "string")
        nullable = spec.get("nullable", False)
        description = spec.get("description", "")
        
        if "enum" in spec:
            enum_values = ", ".join(f'"{v}"' for v in spec["enum"])
            lines.append(f'  "{field}": One of [{enum_values}]{" or null" if nullable else ""} - {description}')
        elif "const" in spec:
            lines.append(f'  "{field}": Must be "{spec["const"]}" - {description}')
        else:
            lines.append(f'  "{field}": {field_type}{" or null" if nullable else ""} - {description}')
    
    return "{\n" + "\n".join(lines) + "\n}"

def validate_extracted_data(data: Dict[str, Any], schema: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate extracted data against schema
    
    Returns:
        (is_valid, list_of_errors)
    """
    errors = []
    
    for field, spec in schema.items():
        # Check required fields
        if field not in data and not spec.get("nullable", False):
            errors.append(f"Missing required field: {field}")
            continue
        
        if field not in data:
            continue
        
        value = data[field]
        
        # Check null values
        if value is None:
            if not spec.get("nullable", False):
                errors.append(f"Field '{field}' cannot be null")
            continue
        
        # Check enums
        if "enum" in spec and value not in spec["enum"]:
            errors.append(f"Field '{field}' has invalid value '{value}'. Must be one of {spec['enum']}")
        
        # Check const
        if "const" in spec and value != spec["const"]:
            errors.append(f"Field '{field}' must be '{spec['const']}', got '{value}'")
        
        # Check type
        expected_type = spec.get("type")
        if expected_type == "string" and not isinstance(value, str):
            errors.append(f"Field '{field}' must be string, got {type(value).__name__}")
        elif expected_type == "boolean" and not isinstance(value, bool):
            errors.append(f"Field '{field}' must be boolean, got {type(value).__name__}")
    
    return len(errors) == 0, errors