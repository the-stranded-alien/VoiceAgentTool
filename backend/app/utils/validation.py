from typing import Dict, Any, List, Tuple
import re

class DataValidator:
    """Validation utilities for call data"""
    
    @staticmethod
    def validate_phone_number(phone: str) -> Tuple[bool, str]:
        """
        Validate phone number format
        
        Returns:
            (is_valid, error_message)
        """
        # Remove formatting
        digits = re.sub(r'\D', '', phone)
        
        if len(digits) < 10:
            return False, "Phone number too short"
        if len(digits) > 11:
            return False, "Phone number too long"
        if len(digits) == 11 and digits[0] != '1':
            return False, "Invalid country code"
        
        return True, ""
    
    @staticmethod
    def validate_load_number(load_number: str) -> Tuple[bool, str]:
        """
        Validate load number format
        
        Returns:
            (is_valid, error_message)
        """
        if not load_number or len(load_number.strip()) == 0:
            return False, "Load number cannot be empty"
        
        if len(load_number) > 50:
            return False, "Load number too long"
        
        return True, ""
    
    @staticmethod
    def validate_structured_data(
        data: Dict[str, Any],
        required_fields: List[str]
    ) -> Tuple[bool, List[str]]:
        """
        Validate that structured data contains required fields
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
            elif data[field] is None:
                errors.append(f"Field '{field}' cannot be null")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def sanitize_input(text: str, max_length: int = 1000) -> str:
        """
        Sanitize user input
        
        Args:
            text: Input text
            max_length: Maximum allowed length
            
        Returns:
            Sanitized text
        """
        # Remove any potentially dangerous characters
        sanitized = text.strip()
        
        # Truncate if too long
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized


# Convenience functions
def is_valid_phone(phone: str) -> bool:
    valid, _ = DataValidator.validate_phone_number(phone)
    return valid

def is_valid_load_number(load_number: str) -> bool:
    valid, _ = DataValidator.validate_load_number(load_number)
    return valid

def sanitize(text: str) -> str:
    return DataValidator.sanitize_input(text)