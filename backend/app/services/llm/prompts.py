from typing import Dict, Any, Optional

class PromptTemplates:
    """Centralized prompt templates for various tasks"""
    
    @staticmethod
    def build_agent_prompt(
        system_prompt: str,
        driver_name: str,
        load_number: str,
        conversation_history: Optional[str] = None
    ) -> str:
        """
        Build dynamic prompt for agent conversation
        
        Args:
            system_prompt: Agent's system prompt with placeholders
            driver_name: Driver's name
            load_number: Load number
            conversation_history: Previous conversation context
            
        Returns:
            Formatted prompt with variables replaced
        """
        # Replace placeholders
        prompt = system_prompt.replace("{driver_name}", driver_name)
        prompt = prompt.replace("{load_number}", load_number)
        
        # Add conversation history if available
        if conversation_history:
            prompt += f"\n\nCONVERSATION SO FAR:\n{conversation_history}"
        
        return prompt
    
    @staticmethod
    def summarize_call(transcript: str, max_words: int = 100) -> str:
        """Generate prompt for call summarization"""
        return f"""Summarize this call transcript in {max_words} words or less:

{transcript}

Focus on:
1. Main purpose of the call
2. Key information exchanged
3. Final outcome or next steps

Summary:"""
    
    @staticmethod
    def generate_response(
        agent_config: Dict[str, Any],
        user_input: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Generate prompt for agent response generation
        
        Args:
            agent_config: Agent configuration with system prompt
            user_input: What the driver said
            context: Additional context (location, history, etc.)
            
        Returns:
            Prompt for generating agent response
        """
        system_prompt = agent_config.get("system_prompt", "")
        driver_name = context.get("driver_name", "Driver")
        load_number = context.get("load_number", "Unknown")
        conversation_history = context.get("conversation_history", "")
        
        prompt = PromptTemplates.build_agent_prompt(
            system_prompt=system_prompt,
            driver_name=driver_name,
            load_number=load_number,
            conversation_history=conversation_history
        )
        
        return f"""{prompt}

DRIVER SAID: "{user_input}"

Generate your response as the agent. Keep it natural, concise (1-2 sentences), and follow the guidelines above.

YOUR RESPONSE:"""
    
    @staticmethod
    def improve_transcript(raw_transcript: str) -> str:
        """Generate prompt for transcript improvement/formatting"""
        return f"""Format and clean up this raw call transcript:

{raw_transcript}

Make it readable by:
1. Clearly labeling speakers (Dispatcher: / Driver:)
2. Fixing obvious transcription errors
3. Adding proper punctuation
4. Removing filler words only if excessive
5. Keeping the content and meaning identical

FORMATTED TRANSCRIPT:"""
    
    @staticmethod
    def extract_intent(user_input: str) -> str:
        """Generate prompt for intent classification"""
        return f"""Classify the intent of this driver's statement:

"{user_input}"

Return ONLY one of these intents:
- status_update: Sharing their current status or location
- emergency: Reporting an emergency or urgent issue
- question: Asking a question
- confirmation: Confirming or acknowledging something
- refusal: Refusing to provide information
- unclear: Statement is unclear or ambiguous

INTENT:"""
    
    @staticmethod
    def handle_edge_case(
        edge_case_type: str,
        context: Dict[str, Any]
    ) -> str:
        """Generate prompt for handling edge cases"""
        templates = {
            "uncooperative": """The driver is giving one-word answers or being uncooperative.
Current response count: {response_count}
Previous attempts: {previous_attempts}

Generate a polite but firm follow-up that requests more specific information.
Keep it professional and understanding of their time.""",
            
            "garbled": """The speech-to-text system couldn't clearly transcribe the driver's response.
Attempt number: {attempt_number}
Garbled text: {garbled_text}

Generate a polite request for them to repeat, speaking more clearly.""",
            
            "location_conflict": """There's a discrepancy between the driver's stated location and GPS data.
Driver said: {driver_location}
GPS shows: {gps_location}

Generate a non-confrontational question to clarify which is correct."""
        }
        
        template = templates.get(edge_case_type, "")
        for key, value in context.items():
            template = template.replace(f"{{{key}}}", str(value))
        
        return template


# Convenience functions
def build_agent_prompt(system_prompt: str, driver_name: str, load_number: str, 
                       conversation_history: Optional[str] = None) -> str:
    return PromptTemplates.build_agent_prompt(
        system_prompt, driver_name, load_number, conversation_history
    )

def generate_response_prompt(agent_config: Dict[str, Any], user_input: str, 
                             context: Dict[str, Any]) -> str:
    return PromptTemplates.generate_response(agent_config, user_input, context)