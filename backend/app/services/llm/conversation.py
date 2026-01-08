from typing import Dict, Any, List, Optional
import logging
from app.services.llm.base import get_llm_client
from app.services.llm.prompts import PromptTemplates

logger = logging.getLogger(__name__)

class ConversationHandler:
    """Handle real-time conversation generation for voice agents"""
    
    def __init__(self):
        self.llm = get_llm_client()
        self.prompts = PromptTemplates()
    
    async def generate_agent_response(
        self,
        agent_config: Dict[str, Any],
        user_input: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Generate agent's next response based on user input
        
        Args:
            agent_config: Agent configuration with system prompt
            user_input: What the driver just said
            context: Call context (driver name, load, history, etc.)
            
        Returns:
            Agent's response text
        """
        try:
            # Build prompt
            prompt = self.prompts.generate_response(
                agent_config=agent_config,
                user_input=user_input,
                context=context
            )
            
            # Generate response
            response = await self.llm.generate_text(
                prompt=prompt,
                temperature=0.3  # Slightly creative but mostly consistent
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating agent response: {str(e)}")
            return "I'm having trouble processing that. Could you repeat?"
    
    async def classify_intent(self, user_input: str) -> str:
        """
        Classify the intent of user's input
        
        Returns: status_update, emergency, question, confirmation, refusal, unclear
        """
        try:
            prompt = self.prompts.extract_intent(user_input)
            intent = await self.llm.generate_text(
                prompt=prompt,
                temperature=0.0
            )
            return intent.strip().lower()
        except Exception as e:
            logger.error(f"Error classifying intent: {str(e)}")
            return "unclear"
    
    async def handle_edge_case(
        self,
        edge_case_type: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Generate appropriate response for edge cases
        
        Args:
            edge_case_type: Type of edge case (uncooperative, garbled, location_conflict)
            context: Relevant context for the edge case
            
        Returns:
            Appropriate agent response
        """
        try:
            prompt = self.prompts.handle_edge_case(edge_case_type, context)
            response = await self.llm.generate_text(
                prompt=prompt,
                temperature=0.2
            )
            return response.strip()
        except Exception as e:
            logger.error(f"Error handling edge case: {str(e)}")
            return "I apologize for the confusion. Let me connect you with someone who can help."
    
    async def improve_transcript(self, raw_transcript: str) -> str:
        """Clean up and format a raw transcript"""
        try:
            prompt = self.prompts.improve_transcript(raw_transcript)
            improved = await self.llm.generate_text(
                prompt=prompt,
                temperature=0.0
            )
            return improved.strip()
        except Exception as e:
            logger.error(f"Error improving transcript: {str(e)}")
            return raw_transcript  # Return original if improvement fails
    
    async def summarize_call(
        self,
        transcript: str,
        max_words: int = 100
    ) -> str:
        """Generate a brief summary of the call"""
        try:
            prompt = self.prompts.summarize_call(transcript, max_words)
            summary = await self.llm.generate_text(
                prompt=prompt,
                temperature=0.1
            )
            return summary.strip()
        except Exception as e:
            logger.error(f"Error summarizing call: {str(e)}")
            return "Summary unavailable"


# Singleton instance
_conversation_handler = None

def get_conversation_handler() -> ConversationHandler:
    """Get or create conversation handler singleton"""
    global _conversation_handler
    if _conversation_handler is None:
        _conversation_handler = ConversationHandler()
    return _conversation_handler