from typing import Dict, Any, Optional
import logging
from app.services.llm.base import get_llm_client
from app.services.llm.schemas import (
    get_schema_for_scenario,
    get_schema_description,
    validate_extracted_data
)

logger = logging.getLogger(__name__)

class StructuredDataExtractor:
    """Extract structured data from call transcripts using Claude"""
    
    def __init__(self):
        self.llm = get_llm_client()
    
    async def extract_from_transcript(
        self,
        transcript: str,
        scenario_type: str,
        driver_name: Optional[str] = None,
        load_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract structured data from a call transcript
        
        Args:
            transcript: Full conversation transcript
            scenario_type: Type of scenario (check_in, emergency, delivery)
            driver_name: Driver's name (for context)
            load_number: Load number (for context)
            
        Returns:
            Dictionary of extracted structured data
        """
        try:
            # Get schema for this scenario
            schema = get_schema_for_scenario(scenario_type)
            schema_desc = get_schema_description(schema)
            
            # Build extraction prompt
            system_prompt = self._build_system_prompt(scenario_type)
            user_prompt = self._build_extraction_prompt(
                transcript=transcript,
                schema_desc=schema_desc,
                driver_name=driver_name,
                load_number=load_number
            )
            
            # Extract data using Claude
            extracted_data = await self.llm.generate_json(
                prompt=user_prompt,
                system=system_prompt,
                schema=schema,
                max_retries=3
            )
            
            # Validate extracted data
            is_valid, errors = validate_extracted_data(extracted_data, schema)
            
            if not is_valid:
                logger.warning(f"Validation errors in extracted data: {errors}")
                # Still return the data but log the issues
                extracted_data["_validation_errors"] = errors
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error extracting structured data: {str(e)}")
            # Return minimal data with error flag
            return {
                "call_outcome": "Extraction Failed",
                "error": str(e),
                "raw_transcript": transcript[:500]  # Include snippet for debugging
            }
    
    def _build_system_prompt(self, scenario_type: str) -> str:
        """Build system prompt for extraction based on scenario"""
        base_prompt = """You are a data extraction specialist for a logistics call center. 
Your job is to analyze call transcripts and extract structured data with high accuracy.

CRITICAL RULES:
1. Return ONLY valid JSON matching the exact schema provided
2. Use null for any missing information
3. Be precise - extract exact values from the transcript
4. Do not make up or infer information that isn't explicitly stated
5. Pay special attention to locations, times, and status keywords
"""
        
        scenario_specific = {
            "check_in": """
SCENARIO: Driver Check-In Call
Focus on:
- Whether driver is in-transit or has arrived
- Current location and ETA if in-transit
- Unloading status and dock information if arrived
- Any delays or issues mentioned
- Whether POD reminder was acknowledged
""",
            "emergency": """
SCENARIO: Emergency Call
Focus on:
- Type of emergency (accident, breakdown, medical, other)
- Safety status of driver and others
- Any injuries reported
- Exact location of emergency
- Whether load is secure
- This should ALWAYS result in escalation
""",
            "delivery": """
SCENARIO: Delivery Confirmation
Focus on:
- Whether delivery was completed successfully
- Time of delivery
- POD receipt confirmation
- POD number if provided
- Any delivery issues
"""
        }
        
        return base_prompt + scenario_specific.get(scenario_type, "")
    
    def _build_extraction_prompt(
        self,
        transcript: str,
        schema_desc: str,
        driver_name: Optional[str],
        load_number: Optional[str]
    ) -> str:
        """Build user prompt for extraction"""
        context = ""
        if driver_name:
            context += f"Driver: {driver_name}\n"
        if load_number:
            context += f"Load: {load_number}\n"
        
        prompt = f"""Extract structured data from this logistics call transcript.

{context}
TRANSCRIPT:
{transcript}

EXTRACT THE FOLLOWING DATA AS JSON:
{schema_desc}

IMPORTANT: 
- Return ONLY the JSON object, no other text
- Use exact values from the transcript
- Use null for missing information
- Be precise with quotes, locations, and times
"""
        return prompt
    
    async def classify_call_outcome(self, transcript: str) -> str:
        """
        Classify the overall outcome of a call
        
        Returns one of: "Successful", "Emergency", "Failed", "Incomplete"
        """
        system_prompt = """You are a call classifier. Analyze the transcript and determine the call outcome.
Return ONLY one word: Successful, Emergency, Failed, or Incomplete"""
        
        user_prompt = f"""Classify this call transcript:

{transcript}

Return ONLY one of these outcomes:
- Successful: Call completed normally with information collected
- Emergency: Emergency situation detected
- Failed: Call failed due to technical issues or uncooperative driver
- Incomplete: Call ended without completing objectives"""
        
        try:
            outcome = await self.llm.generate_text(
                prompt=user_prompt,
                system=system_prompt,
                temperature=0.0
            )
            return outcome.strip()
        except Exception as e:
            logger.error(f"Error classifying call outcome: {str(e)}")
            return "Unknown"
    
    async def detect_emergency_keywords(self, text: str) -> bool:
        """
        Detect if text contains emergency keywords
        
        Returns True if emergency detected
        """
        emergency_keywords = [
            "accident", "crash", "collision", "injured", "injury",
            "breakdown", "blowout", "emergency", "help", "danger",
            "medical", "ambulance", "hospital", "hurt", "pain"
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in emergency_keywords)


# Singleton instance
_extractor = None

def get_extractor() -> StructuredDataExtractor:
    """Get or create extractor singleton"""
    global _extractor
    if _extractor is None:
        _extractor = StructuredDataExtractor()
    return _extractor