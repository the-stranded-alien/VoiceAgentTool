from retell import Retell
from retell.types import AgentResponse, CallResponse, PhoneNumberResponse
from typing import Optional, List, Dict, Any
import logging
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class RetellClientWrapper:
    """
    Wrapper around Retell SDK for easier use in our application
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Retell client with SDK"""
        self.api_key = api_key or settings.retell_api_key
        self.client = Retell(api_key=self.api_key)
        logger.info("Retell SDK client initialized")
    
    # ==================== Agent Management ====================
    
    def create_agent(
        self,
        agent_name: str,
        voice_id: str = "11labs-Adrian",
        language: str = "en-US",
        responsiveness: float = 0.8,
        interruption_sensitivity: float = 1.0,
        enable_backchannel: bool = True,
        backchannel_frequency: float = 0.8,
        backchannel_words: Optional[List[str]] = None,
        reminder_trigger_ms: int = 10000,
        reminder_max_count: int = 2,
        ambient_sound: Optional[str] = None,
        pronunciation_dictionary: Optional[List[Dict[str, str]]] = None,
        llm_websocket_url: Optional[str] = None,
        **kwargs
    ) -> AgentResponse:
        """
        Create a new agent using Retell SDK

        Args:
            agent_name: Name of the agent
            voice_id: Voice ID from Retell's voice library
            language: Language code (e.g., "en-US")
            responsiveness: Agent response speed/delay (0-1, higher = faster)
            interruption_sensitivity: How easily agent can be interrupted (0-1)
            enable_backchannel: Enable "uh-huh", "I see" responses
            backchannel_frequency: How often to backchannel (0-1)
            backchannel_words: Custom backchannel words
            reminder_trigger_ms: Time before reminder (milliseconds)
            reminder_max_count: Max number of reminders
            ambient_sound: Background sound ("coffee-shop", "call-center", None)
            pronunciation_dictionary: Custom pronunciation rules
            llm_websocket_url: URL for custom LLM websocket

        Returns:
            AgentResponse object from Retell SDK
        """
        try:
            # Build response_engine (REQUIRED parameter)
            if llm_websocket_url:
                # Custom LLM response engine
                response_engine = {
                    "type": "custom-llm",
                    "llm_websocket_url": llm_websocket_url
                }
            else:
                # Need to provide a response engine - raise error if not provided
                raise ValueError("llm_websocket_url is required for custom LLM response engine")

            # Build agent configuration
            agent_config = {
                "response_engine": response_engine,
                "agent_name": agent_name,
                "voice_id": voice_id,
                "language": language,
                "responsiveness": responsiveness,
                "interruption_sensitivity": interruption_sensitivity,
                "enable_backchannel": enable_backchannel,
                "backchannel_frequency": backchannel_frequency,
                "reminder_trigger_ms": reminder_trigger_ms,
                "reminder_max_count": reminder_max_count,
            }

            # Add optional parameters
            if backchannel_words:
                agent_config["backchannel_words"] = backchannel_words

            if ambient_sound:
                agent_config["ambient_sound"] = ambient_sound

            if pronunciation_dictionary:
                agent_config["pronunciation_dictionary"] = pronunciation_dictionary

            # Merge any additional kwargs
            agent_config.update(kwargs)

            # Create agent using SDK
            agent = self.client.agent.create(**agent_config)

            logger.info(f"Created Retell agent: {agent.agent_id}")
            return agent

        except Exception as e:
            logger.error(f"Failed to create agent: {str(e)}")
            raise
    
    def get_agent(self, agent_id: str) -> AgentResponse:
        """Get agent by ID"""
        try:
            return self.client.agent.retrieve(agent_id)
        except Exception as e:
            logger.error(f"Failed to get agent {agent_id}: {str(e)}")
            raise
    
    def update_agent(self, agent_id: str, **updates) -> AgentResponse:
        """Update agent configuration"""
        try:
            return self.client.agent.update(agent_id, **updates)
        except Exception as e:
            logger.error(f"Failed to update agent {agent_id}: {str(e)}")
            raise
    
    def delete_agent(self, agent_id: str) -> None:
        """Delete an agent"""
        try:
            self.client.agent.delete(agent_id)
            logger.info(f"Deleted agent: {agent_id}")
        except Exception as e:
            logger.error(f"Failed to delete agent {agent_id}: {str(e)}")
            raise
    
    def list_agents(self) -> List[AgentResponse]:
        """List all agents"""
        try:
            response = self.client.agent.list()
            return response
        except Exception as e:
            logger.error(f"Failed to list agents: {str(e)}")
            raise
    
    # ==================== Call Management ====================
    
    def create_phone_call(
        self,
        from_number: str,
        to_number: str,
        agent_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        retell_llm_dynamic_variables: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> CallResponse:
        """
        Create a phone call
        
        Args:
            from_number: Retell phone number to call from
            to_number: Destination phone number
            agent_id: Agent ID to use for the call
            metadata: Custom metadata (max 1KB)
            retell_llm_dynamic_variables: Variables for prompt customization
            
        Returns:
            RegisterCallResponse with call_id and other details
        """
        try:
            call_params = {
                "from_number": from_number,
                "to_number": to_number,
                "override_agent_id": agent_id,
            }
            
            if metadata:
                call_params["metadata"] = metadata
            
            if retell_llm_dynamic_variables:
                call_params["retell_llm_dynamic_variables"] = retell_llm_dynamic_variables
            
            # Merge additional kwargs
            call_params.update(kwargs)
            
            # Create call using SDK
            response = self.client.call.register(**call_params)
            
            logger.info(f"Created phone call: {response.call_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create phone call: {str(e)}")
            raise
    
    def create_web_call(
        self,
        agent_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        retell_llm_dynamic_variables: Optional[Dict[str, Any]] = None,
    ) -> CallResponse:
        """
        Create a web call for browser-based testing
        
        Args:
            agent_id: Agent ID to use
            metadata: Custom metadata
            retell_llm_dynamic_variables: Variables for prompt customization
            
        Returns:
            RegisterCallResponse with call_id and access_token for web SDK
        """
        try:
            call_params = {
                "agent_id": agent_id,
            }
            
            if metadata:
                call_params["metadata"] = metadata
            
            if retell_llm_dynamic_variables:
                call_params["retell_llm_dynamic_variables"] = retell_llm_dynamic_variables
            
            # Create web call
            response = self.client.call.create_web_call(**call_params)
            
            logger.info(f"Created web call: {response.call_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create web call: {str(e)}")
            raise
    
    def get_call(self, call_id: str):
        """Get call details by ID"""
        try:
            return self.client.call.retrieve(call_id)
        except Exception as e:
            logger.error(f"Failed to get call {call_id}: {str(e)}")
            raise
    
    def list_calls(
        self,
        filter_criteria: Optional[Dict[str, Any]] = None,
        limit: int = 1000,
        sort_order: str = "descending"
    ):
        """
        List calls with optional filtering
        
        Args:
            filter_criteria: Filter by agent_id, call_type, etc.
            limit: Max number of calls to return
            sort_order: "ascending" or "descending"
        """
        try:
            params = {
                "limit": limit,
                "sort_order": sort_order
            }
            
            if filter_criteria:
                params["filter_criteria"] = filter_criteria
            
            return self.client.call.list(**params)
        except Exception as e:
            logger.error(f"Failed to list calls: {str(e)}")
            raise
    
    # ==================== Phone Number Management ====================
    
    def list_phone_numbers(self) -> List[PhoneNumberResponse]:
        """List all phone numbers in your Retell account"""
        try:
            response = self.client.phone_number.list()
            return response
        except Exception as e:
            logger.error(f"Failed to list phone numbers: {str(e)}")
            raise
    
    def get_phone_number(self, phone_number_id: str) -> PhoneNumberResponse:
        """Get details of a specific phone number"""
        try:
            return self.client.phone_number.retrieve(phone_number_id)
        except Exception as e:
            logger.error(f"Failed to get phone number: {str(e)}")
            raise


# Singleton instance
_retell_client = None

def get_retell_client() -> RetellClientWrapper:
    """Get or create Retell client singleton"""
    global _retell_client
    if _retell_client is None:
        _retell_client = RetellClientWrapper()
    return _retell_client