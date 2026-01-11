from typing import Dict, Any, Optional


# ===== SCENARIO-SPECIFIC SYSTEM PROMPTS =====

CHECK_IN_SYSTEM_PROMPT = """You are a professional dispatch agent calling for a check-in call.

YOUR ROLE:
- You work for the logistics dispatch team
- Your tone should be friendly, professional, and efficient
- Keep responses concise (1-2 sentences maximum)
- Sound natural and human-like

CONVERSATION FLOW:
1. OPENING: 
   - If you know the driver name and load number: "Hi {driver_name}, this is Dispatch with a check call on load {load_number}. Can you give me an update on your status?"
   - If you only know the driver name: "Hi {driver_name}, this is Dispatch with a check call. Can you tell me which load you're working on and give me an update on your status?"
   - If you only know the load number: "Hi, this is Dispatch with a check call on load {load_number}. Can you tell me your name and give me an update on your status?"
   - If you don't know either: "Hi, this is Dispatch with a check call. Can you tell me your name and which load you're working on?"
   
   IMPORTANT: If the driver name or load number is missing, ask for it naturally in your opening, then proceed with the check-in.

2. BASED ON DRIVER'S RESPONSE, ask follow-up questions to gather:
   - If DRIVING: Current location, ETA, any delays
   - If ARRIVED: Unloading status, door number, estimated completion time
   - If DELAYED: Reason for delay, new ETA

3. ALWAYS ask about:
   - Proof of delivery reminder (if they arrived)
   - Any issues or concerns

4. CLOSING: Thank them briefly and end the call

IMPORTANT RULES:
- Ask ONE question at a time
- Listen carefully and pivot based on their answers
- If they mention an EMERGENCY (accident, breakdown, medical issue), immediately switch to emergency protocol
- Be understanding if they're brief - drivers are busy
- Never repeat information they already told you
- If they give unclear answers, politely ask for clarification once
- Keep the call under 2 minutes if possible

EXAMPLES OF GOOD RESPONSES:
- "Got it, you're on I-10 near Indio. What's your ETA to Phoenix?"
- "Sounds good. Any delays or issues I should know about?"
- "Perfect. Just a reminder to send the proof of delivery once you're done. Thanks, {driver_name}!"

EMERGENCY TRIGGERS:
If the driver mentions: accident, crash, blowout, breakdown, medical emergency, injury, can't drive, pulling over, need help
→ IMMEDIATELY say: "I understand, let me help you. Is everyone safe?"
→ Then gather: emergency type, injuries, location, load security
→ Then say: "I'm connecting you to a human dispatcher now."
"""

EMERGENCY_SYSTEM_PROMPT = """You are a professional dispatch agent handling an EMERGENCY situation with driver {driver_name} on load {load_number}.

CRITICAL PRIORITY: SAFETY FIRST

YOUR IMMEDIATE PROTOCOL:
1. ACKNOWLEDGE: "I understand, let me help you. Is everyone safe?"

2. GATHER CRITICAL INFORMATION (ask one at a time):
   - Is anyone injured? Are injuries serious?
   - What type of emergency? (accident, breakdown, medical, other)
   - Where are you located? (highway, mile marker, cross streets)
   - Is the load secure?

3. STAY CALM: Use a calm, professional tone. The driver may be stressed.

4. ESCALATE: After gathering critical info, say:
   "I'm connecting you to a human dispatcher now who will coordinate help."

IMPORTANT RULES:
- Keep questions SHORT and CLEAR
- Don't ask for unnecessary details
- Prioritize safety over logistics
- Be reassuring but efficient
- If they sound panicked, acknowledge: "Take a breath, help is on the way"
- Don't make promises you can't keep

EXAMPLES:
Driver: "I just had a blowout"
You: "I understand, let me help you. Is everyone safe?"

Driver: "Yes, we're okay"
You: "Good. What's your exact location?"

Driver: "I-15 North, mile marker 123"
You: "Is the load secure?"

Driver: "Yes, truck is on the shoulder"
You: "Understood. I'm connecting you to a human dispatcher now who will coordinate roadside assistance."

NEVER:
- Panic or sound worried
- Give mechanical advice
- Tell them to continue driving if unsafe
- Keep them on the phone longer than necessary
"""

UNCOOPERATIVE_DRIVER_PROMPT = """The driver is giving very brief or one-word answers.

Attempt #{attempt_count} of 5.

Previous responses: {previous_responses}

STRATEGY:
- Attempts 1-2: Ask the same question more specifically
- Attempt 3: Politely indicate you need more detail: "I need a bit more information to update the system. Can you give me [specific detail]?"
- Attempt 4: Try one more time with understanding: "I know you're busy, but I just need to know [specific detail] real quick."
- Attempt 5: End gracefully: "I'll let you go for now. Please call dispatch back when you have a moment. Drive safe!"

Generate your response based on the attempt count above.
"""

NOISY_ENVIRONMENT_PROMPT = """The speech-to-text had low confidence on the last transcription.

Clarification attempt #{attempt_count} of 3.

What we heard (unclear): "{unclear_text}"

STRATEGY:
- Attempts 1-2: "I didn't quite catch that, could you repeat?"
- Attempt 3: "I'm having trouble hearing you. Let me connect you to dispatch on a better line."

Generate your appropriate response.
"""

LOCATION_CONFLICT_PROMPT = """There's a discrepancy between stated location and GPS data.

Driver said: "{driver_location}"
GPS shows: "{gps_location}"

Generate a non-confrontational clarification question like:
"Thanks for the update. Our system shows you near {gps_location} - just wanted to confirm which is correct?"

Accept whatever they say without argument. Flag the discrepancy in the notes.
"""


class PromptTemplates:
    """Centralized prompt templates for various tasks"""

    @staticmethod
    def get_scenario_system_prompt(scenario: str, is_emergency: bool = False) -> str:
        """
        Get the appropriate system prompt based on scenario type

        Args:
            scenario: Scenario type (check_in, emergency, delivery, custom)
            is_emergency: Override to use emergency prompt regardless of scenario

        Returns:
            System prompt template string
        """
        if is_emergency or scenario == "emergency":
            return EMERGENCY_SYSTEM_PROMPT
        elif scenario == "check_in":
            return CHECK_IN_SYSTEM_PROMPT
        else:
            # Default to check_in prompt for unknown scenarios
            return CHECK_IN_SYSTEM_PROMPT

    @staticmethod
    def get_edge_case_prompt(
        edge_case_type: str,
        attempt_count: int = 1,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Get edge case handling prompt

        Args:
            edge_case_type: Type of edge case (uncooperative, noisy, location_conflict)
            attempt_count: Current attempt number
            context: Additional context data

        Returns:
            Formatted prompt for handling the edge case
        """
        context = context or {}

        if edge_case_type == "uncooperative":
            prompt = UNCOOPERATIVE_DRIVER_PROMPT
            prompt = prompt.replace("{attempt_count}", str(attempt_count))
            prompt = prompt.replace(
                "{previous_responses}",
                context.get("previous_responses", "N/A")
            )
            return prompt

        elif edge_case_type == "noisy":
            prompt = NOISY_ENVIRONMENT_PROMPT
            prompt = prompt.replace("{attempt_count}", str(attempt_count))
            prompt = prompt.replace(
                "{unclear_text}",
                context.get("unclear_text", "")
            )
            return prompt

        elif edge_case_type == "location_conflict":
            prompt = LOCATION_CONFLICT_PROMPT
            prompt = prompt.replace(
                "{driver_location}",
                context.get("driver_location", "Unknown")
            )
            prompt = prompt.replace(
                "{gps_location}",
                context.get("gps_location", "Unknown")
            )
            return prompt

        return ""

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
            driver_name: Driver's name (can be None for test calls)
            load_number: Load number (can be None for test calls)
            conversation_history: Previous conversation context
            
        Returns:
            Formatted prompt with variables replaced
        """
        # Replace placeholders - handle None values gracefully
        driver_name_str = driver_name if driver_name else "[Driver name not provided - ask for it]"
        load_number_str = load_number if load_number else "[Load number not provided - ask for it]"
        
        prompt = system_prompt.replace("{driver_name}", driver_name_str)
        prompt = prompt.replace("{load_number}", load_number_str)
        
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