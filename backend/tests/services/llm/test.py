import asyncio
from app.services.llm.extractor import get_extractor
from app.services.llm.conversation import get_conversation_handler

# Sample transcript for testing
SAMPLE_TRANSCRIPT = """
Dispatcher: Hi Mike, this is Dispatch with a check call on load 7891-B. Can you give me an update on your status?

Mike: Hey, yeah I'm currently on I-10, just passed Indio.

Dispatcher: Got it. What's your ETA to Phoenix?

Mike: Should be there tomorrow morning around 8 AM, traffic's been good.

Dispatcher: Perfect. Any delays or issues I should know about?

Mike: Nope, smooth sailing so far.

Dispatcher: Great. Just a reminder to grab the POD when you arrive.

Mike: Will do, thanks.

Dispatcher: Thanks Mike, drive safe.
"""

async def test_extraction():
    """Test structured data extraction"""
    print("Testing structured data extraction...")
    print("=" * 60)
    
    extractor = get_extractor()
    
    result = await extractor.extract_from_transcript(
        transcript=SAMPLE_TRANSCRIPT,
        scenario_type="check_in",
        driver_name="Mike",
        load_number="7891-B"
    )
    
    print("Extracted Data:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    print()

async def test_conversation():
    """Test conversation generation"""
    print("Testing conversation generation...")
    print("=" * 60)
    
    handler = get_conversation_handler()
    
    agent_config = {
        "system_prompt": "You are a professional dispatcher. Keep responses brief and friendly."
    }
    
    context = {
        "driver_name": "Mike",
        "load_number": "7891-B",
        "conversation_history": ""
    }
    
    user_input = "I'm on I-10 near Palm Springs"
    
    response = await handler.generate_agent_response(
        agent_config=agent_config,
        user_input=user_input,
        context=context
    )
    
    print(f"Driver: {user_input}")
    print(f"Agent: {response}")
    print()

async def main():
    await test_extraction()
    await test_conversation()

if __name__ == "__main__":
    asyncio.run(main())