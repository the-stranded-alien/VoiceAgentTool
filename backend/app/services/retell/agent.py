from typing import Dict, Any, Optional
import logging
from app.services.retell.client import get_retell_client
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class RetellAgentService:
    """Service for managing Retell AI agents using SDK"""
    
    def __init__(self):
        self.client = get_retell_client()
    
    def create_agent_from_config(
        self,
        agent_config: Dict[str, Any]
    ) -> str:
        """
        Create a Retell AI agent from our internal agent configuration
        
        Args:
            agent_config: Our internal agent configuration dict
            
        Returns:
            Retell agent ID (string)
        """
        try:
            # Extract settings
            name = agent_config.get("name", "Logistics Agent")
            voice_settings = agent_config.get("voice_settings", {})
            advanced_settings = agent_config.get("advanced_settings", {})
            
            # Map voice settings to Retell SDK parameters
            voice_id = voice_settings.get("voice_id", "11labs-Adrian")
            # Map "default" to a valid Retell voice ID
            if voice_id == "default":
                voice_id = "11labs-Adrian"
            
            responsiveness = voice_settings.get("responsiveness", 0.8)
            interruption_sensitivity = voice_settings.get("interruption_sensitivity", 0.7)
            
            # Backchannel settings
            backchannel_config = voice_settings.get("backchannel", {})
            enable_backchannel = backchannel_config.get("enabled", True)
            backchannel_frequency = self._map_backchannel_frequency(
                backchannel_config.get("frequency", "medium")
            )
            
            # Custom backchannel words
            backchannel_words = backchannel_config.get("words")
            if backchannel_words and isinstance(backchannel_words, list):
                backchannel_words = backchannel_words
            else:
                backchannel_words = ["uh-huh", "I see", "okay", "got it", "mm-hmm"]
            
            # Filler words
            filler_config = voice_settings.get("filler_words", {})
            # Note: Retell SDK handles filler words automatically based on voice model
            
            # Ambient sound
            ambient_sound = None
            if voice_settings.get("ambient_sound"):
                ambient_sound = "office"  # Options: "coffee-shop", "office"
            
            # Language
            language = voice_settings.get("language", "en-US")
            
            # LLM Websocket URL for custom LLM integration
            # WebSocket routes are mounted at /ws prefix (see main.py)
            llm_websocket_url = f"{settings.server_url}/ws/llm"
            
            # Create agent using SDK
            agent = self.client.create_agent(
                agent_name=name,
                voice_id=voice_id,
                language=language,
                responsiveness=responsiveness,
                interruption_sensitivity=interruption_sensitivity,
                enable_backchannel=enable_backchannel,
                backchannel_frequency=backchannel_frequency,
                backchannel_words=backchannel_words,
                ambient_sound=ambient_sound,
                llm_websocket_url=llm_websocket_url,
                # Reminder settings
                reminder_trigger_ms=10000,  # 10 seconds
                reminder_max_count=2,
            )
            
            logger.info(f"Created Retell agent '{name}': {agent.agent_id}")
            return agent.agent_id
            
        except Exception as e:
            logger.error(f"Failed to create Retell agent: {str(e)}")
            raise
    
    def _map_interruption_sensitivity(self, sensitivity: float) -> int:
        """
        Map our 0.0-1.0 sensitivity to Retell's 0-1 integer scale
        
        Args:
            sensitivity: Float from 0.0 (least sensitive) to 1.0 (most sensitive)
            
        Returns:
            Integer 0 or 1
        """
        return 1 if sensitivity >= 0.5 else 0
    
    def _map_backchannel_frequency(self, frequency: str) -> float:
        """
        Map frequency string to Retell's 0.0-1.0 scale
        
        Args:
            frequency: "low", "medium", or "high"
            
        Returns:
            Float from 0.0 to 1.0
        """
        mapping = {
            "low": 0.3,
            "medium": 0.8,
            "high": 1.0
        }
        return mapping.get(frequency.lower(), 0.8)
    
    def update_agent(
        self,
        retell_agent_id: str,
        **updates
    ) -> str:
        """
        Update an existing Retell agent
        
        Args:
            retell_agent_id: Retell agent ID
            **updates: Fields to update
            
        Returns:
            Updated agent ID
        """
        try:
            agent = self.client.update_agent(retell_agent_id, **updates)
            logger.info(f"Updated agent: {agent.agent_id}")
            return agent.agent_id
        except Exception as e:
            logger.error(f"Failed to update agent: {str(e)}")
            raise
    
    def delete_agent(self, retell_agent_id: str) -> bool:
        """
        Delete a Retell agent
        
        Args:
            retell_agent_id: Retell agent ID
            
        Returns:
            True if successful
        """
        try:
            self.client.delete_agent(retell_agent_id)
            logger.info(f"Deleted agent: {retell_agent_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete agent: {str(e)}")
            return False
    
    def get_agent(self, retell_agent_id: str):
        """Get agent details"""
        try:
            return self.client.get_agent(retell_agent_id)
        except Exception as e:
            logger.error(f"Failed to get agent: {str(e)}")
            raise
    
    def list_agents(self):
        """List all agents"""
        try:
            return self.client.list_agents()
        except Exception as e:
            logger.error(f"Failed to list agents: {str(e)}")
            raise


# Singleton
_agent_service = None

def get_retell_agent_service() -> RetellAgentService:
    """Get or create agent service singleton"""
    global _agent_service
    if _agent_service is None:
        _agent_service = RetellAgentService()
    return _agent_service