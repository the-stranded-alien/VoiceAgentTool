"""
Simple WebSocket client to test Retell AI Custom LLM endpoint

This simulates what Retell AI will send to our WebSocket endpoint
"""

import asyncio
import json
import websockets


async def test_websocket():
    """Test the WebSocket endpoint with simulated Retell messages"""

    uri = "ws://localhost:8000/ws/llm"

    try:
        async with websockets.connect(uri) as websocket:
            print("✓ Connected to WebSocket")

            # 1. Send call_details (simulating call start)
            call_details = {
                "interaction_type": "call_details",
                "call_id": "test_call_123",
                "retell_llm_dynamic_variables": {
                    "call_id": "internal_call_456",
                    "driver_name": "Mike",
                    "load_number": "7891-B",
                    "phone_number": "+1234567890",
                    "scenario": "check_in"
                }
            }

            print("\nSending call_details...")
            await websocket.send(json.dumps(call_details))

            # Receive opening response
            response = await websocket.recv()
            print(f"Received: {response}")
            response_data = json.loads(response)
            print(f"✓ Opening message: {response_data.get('content')}")

            # 2. Send response_required (user's first utterance)
            response_required = {
                "interaction_type": "response_required",
                "response_id": 1,
                "transcript": [
                    {"role": "agent", "content": response_data.get("content")},
                    {"role": "user", "content": "I'm driving on I-10 near Indio"}
                ]
            }

            print("\nSending response_required (user: 'I'm driving on I-10 near Indio')...")
            await websocket.send(json.dumps(response_required))

            # Receive agent response
            response = await websocket.recv()
            print(f"Received: {response}")
            response_data = json.loads(response)
            print(f"✓ Agent response: {response_data.get('content')}")

            # 3. Test emergency detection
            emergency_utterance = {
                "interaction_type": "response_required",
                "response_id": 2,
                "transcript": [
                    {"role": "agent", "content": response_data.get("content")},
                    {"role": "user", "content": "Wait, I just had a blowout!"}
                ]
            }

            print("\nSending emergency utterance ('I just had a blowout!')...")
            await websocket.send(json.dumps(emergency_utterance))

            # Receive emergency response
            response = await websocket.recv()
            print(f"Received: {response}")
            response_data = json.loads(response)
            print(f"✓ Emergency response: {response_data.get('content')}")

            # Check if emergency was detected
            if "safe" in response_data.get("content", "").lower():
                print("✓ Emergency protocol activated!")
            else:
                print("✗ Emergency not detected")

            print("\n✓ All tests passed!")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_websocket())
