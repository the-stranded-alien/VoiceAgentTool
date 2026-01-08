import re
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

class TextProcessor:
    """Utilities for processing and cleaning text"""
    
    @staticmethod
    def clean_phone_number(phone: str) -> str:
        """
        Clean and format phone number
        
        Args:
            phone: Raw phone number
            
        Returns:
            Formatted phone number
        """
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)
        
        # Format as +1-XXX-XXX-XXXX for US numbers
        if len(digits) == 10:
            return f"+1-{digits[:3]}-{digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"+1-{digits[1:4]}-{digits[4:7]}-{digits[7:]}"
        else:
            return phone  # Return original if can't parse
    
    @staticmethod
    def extract_location(text: str) -> Optional[str]:
        """
        Extract location from text
        
        Looks for patterns like:
        - Interstate mentions (I-10, I-15)
        - Highway mentions (Highway 101, US-50)
        - Mile markers
        - City names
        """
        # Interstate pattern
        interstate = re.search(r'I-?\d+', text, re.IGNORECASE)
        if interstate:
            # Try to get more context
            context = text[max(0, interstate.start()-20):min(len(text), interstate.end()+30)]
            return context.strip()
        
        # Look for "near", "at", "on" followed by location
        location_pattern = r'(?:near|at|on|in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        match = re.search(location_pattern, text)
        if match:
            return match.group(1)
        
        return None
    
    @staticmethod
    def extract_time(text: str) -> Optional[str]:
        """
        Extract time/ETA from text
        
        Looks for patterns like:
        - "8 AM", "3:30 PM"
        - "tomorrow at 8"
        - "in 2 hours"
        """
        # Time patterns
        time_patterns = [
            r'\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)',
            r'\d{1,2}\s*(?:AM|PM|am|pm)',
            r'tomorrow\s+(?:at\s+)?\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm)?',
            r'in\s+\d+\s+(?:hour|minute)s?',
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    @staticmethod
    def detect_emergency_keywords(text: str) -> List[str]:
        """
        Detect emergency keywords in text
        
        Returns list of matched keywords
        """
        emergency_keywords = {
            'accident': ['accident', 'crash', 'collision', 'hit'],
            'breakdown': ['breakdown', 'broke down', 'blowout', 'flat tire', 'engine'],
            'medical': ['medical', 'injured', 'injury', 'hurt', 'pain', 'sick'],
            'emergency': ['emergency', 'help', 'urgent', 'danger']
        }
        
        text_lower = text.lower()
        found = []
        
        for category, keywords in emergency_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    found.append(category)
                    break
        
        return found
    
    @staticmethod
    def extract_yes_no(text: str) -> Optional[bool]:
        """
        Determine if text contains yes/no response
        
        Returns:
            True for yes, False for no, None for unclear
        """
        text_lower = text.lower().strip()
        
        yes_patterns = ['yes', 'yeah', 'yep', 'sure', 'correct', 'right', 'affirmative', 'ok', 'okay']
        no_patterns = ['no', 'nope', 'nah', 'negative', 'incorrect', 'wrong']
        
        if any(pattern in text_lower for pattern in yes_patterns):
            return True
        if any(pattern in text_lower for pattern in no_patterns):
            return False
        
        return None
    
    @staticmethod
    def count_words(text: str) -> int:
        """Count words in text"""
        return len(text.split())
    
    @staticmethod
    def is_short_response(text: str, threshold: int = 5) -> bool:
        """Check if response is suspiciously short (uncooperative driver)"""
        return TextProcessor.count_words(text) <= threshold
    
    @staticmethod
    def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
        """Truncate text to maximum length"""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix


class TranscriptFormatter:
    """Format and structure transcripts"""
    
    @staticmethod
    def format_transcript(
        messages: List[Dict[str, str]],
        speaker_labels: Dict[str, str] = None
    ) -> str:
        """
        Format messages into readable transcript
        
        Args:
            messages: List of {"role": "user/assistant", "content": "..."}
            speaker_labels: Optional custom labels {"user": "Driver", "assistant": "Dispatcher"}
            
        Returns:
            Formatted transcript
        """
        labels = speaker_labels or {"user": "Driver", "assistant": "Dispatcher"}
        
        formatted = []
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            speaker = labels.get(role, role.capitalize())
            formatted.append(f"{speaker}: {content}")
        
        return "\n\n".join(formatted)
    
    @staticmethod
    def add_timestamps(transcript: str) -> str:
        """Add timestamps to transcript lines"""
        lines = transcript.split("\n")
        start_time = datetime.now()
        
        formatted = []
        for i, line in enumerate(lines):
            if line.strip():
                timestamp = start_time + timedelta(seconds=i * 3)  # Estimate 3 sec per exchange
                formatted.append(f"[{timestamp.strftime('%H:%M:%S')}] {line}")
        
        return "\n".join(formatted)


# Convenience functions
def clean_phone(phone: str) -> str:
    return TextProcessor.clean_phone_number(phone)

def detect_emergency(text: str) -> bool:
    return len(TextProcessor.detect_emergency_keywords(text)) > 0

def extract_location(text: str) -> Optional[str]:
    return TextProcessor.extract_location(text)

def format_transcript(messages: List[Dict[str, str]]) -> str:
    return TranscriptFormatter.format_transcript(messages)