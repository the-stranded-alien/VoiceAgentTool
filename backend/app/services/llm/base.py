from anthropic import Anthropic
from app.config import get_settings
from typing import Optional, Dict, Any, List
import json
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

class LLMClient:
    """Base client for interacting with Anthropic's Claude"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = Anthropic(api_key=api_key or settings.anthropic_api_key)
        self.model = settings.llm_model
        self.max_tokens = settings.llm_max_tokens
        self.temperature = settings.llm_temperature
    
    async def generate_text(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate text completion from Claude
        
        Args:
            prompt: User prompt
            system: System prompt (instructions for Claude)
            temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
        """
        try:
            messages = [{"role": "user", "content": prompt}]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature if temperature is not None else self.temperature,
                system=system or "",
                messages=messages
            )
            
            # Extract text from response
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            raise
    
    async def generate_json(
        self,
        prompt: str,
        system: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None,
        max_retries: int = 2
    ) -> Dict[str, Any]:
        """
        Generate structured JSON response from Claude
        
        Args:
            prompt: User prompt
            system: System prompt
            schema: Expected JSON schema (for validation)
            max_retries: Number of retry attempts if JSON parsing fails
            
        Returns:
            Parsed JSON object
        """
        system_with_json = (system or "") + "\n\nIMPORTANT: Return ONLY valid JSON. No markdown, no explanations, no preamble."
        
        for attempt in range(max_retries + 1):
            try:
                text_response = await self.generate_text(
                    prompt=prompt,
                    system=system_with_json,
                    temperature=0.1  # Low temperature for consistent JSON
                )
                
                # Clean up response (remove markdown code blocks if present)
                text_response = text_response.strip()
                if text_response.startswith("```json"):
                    text_response = text_response[7:]
                if text_response.startswith("```"):
                    text_response = text_response[3:]
                if text_response.endswith("```"):
                    text_response = text_response[:-3]
                text_response = text_response.strip()
                
                # Parse JSON
                result = json.loads(text_response)
                
                # Validate against schema if provided
                if schema:
                    self._validate_schema(result, schema)
                
                return result
                
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parsing failed (attempt {attempt + 1}/{max_retries + 1}): {str(e)}")
                if attempt == max_retries:
                    logger.error(f"Failed to parse JSON after {max_retries + 1} attempts")
                    raise ValueError(f"Could not parse valid JSON from response: {text_response[:200]}")
            except Exception as e:
                logger.error(f"Error generating JSON: {str(e)}")
                raise
    
    def _validate_schema(self, data: Dict[str, Any], schema: Dict[str, Any]):
        """Basic schema validation"""
        for key, expected_type in schema.items():
            if key not in data:
                logger.warning(f"Missing expected key: {key}")
            # Add more sophisticated validation as needed
    
    async def generate_with_examples(
        self,
        prompt: str,
        examples: List[Dict[str, str]],
        system: Optional[str] = None
    ) -> str:
        """
        Generate text with few-shot examples
        
        Args:
            prompt: User prompt
            examples: List of {"input": "...", "output": "..."} examples
            system: System prompt
            
        Returns:
            Generated text response
        """
        # Build few-shot prompt
        few_shot_prompt = ""
        for i, example in enumerate(examples, 1):
            few_shot_prompt += f"\nExample {i}:\n"
            few_shot_prompt += f"Input: {example['input']}\n"
            few_shot_prompt += f"Output: {example['output']}\n"
        
        few_shot_prompt += f"\nNow for the actual task:\n{prompt}"
        
        return await self.generate_text(
            prompt=few_shot_prompt,
            system=system
        )


# Singleton instance
_llm_client = None

def get_llm_client() -> LLMClient:
    """Get or create LLM client singleton"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client