"""
Simple test script for webhook endpoint
"""
import asyncio
import httpx

async def test_webhook_endpoint():
    """Test the webhook endpoint with different scenarios"""
    base_url = "http://localhost:8000"

    print("=" * 60)
    print("Testing Webhook Endpoint")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        # Test 1: GET test endpoint
        print("\n1. Testing GET /api/v1/webhook/retell/test...")
        try:
            response = await client.get(f"{base_url}/api/v1/webhook/retell/test")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            print("   ✅ Test endpoint is accessible")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        # Test 2: POST with empty body
        print("\n2. Testing POST /api/v1/webhook/retell with empty body...")
        try:
            response = await client.post(
                f"{base_url}/api/v1/webhook/retell",
                headers={"Content-Type": "application/json"}
            )
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            print("   ✅ Handles empty body correctly")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        # Test 3: POST with invalid JSON
        print("\n3. Testing POST /api/v1/webhook/retell with invalid JSON...")
        try:
            response = await client.post(
                f"{base_url}/api/v1/webhook/retell",
                content="invalid json",
                headers={"Content-Type": "application/json"}
            )
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            print("   ✅ Handles invalid JSON correctly")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        # Test 4: POST with valid Retell webhook payload (call_started)
        print("\n4. Testing POST /api/v1/webhook/retell with call_started event...")
        try:
            payload = {
                "event": "call_started",
                "call": {
                    "call_id": "test-call-123",
                    "agent_id": "test-agent-456",
                    "from_number": "+1234567890",
                    "to_number": "+0987654321",
                    "direction": "outbound",
                    "call_status": "in-progress"
                }
            }
            response = await client.post(
                f"{base_url}/api/v1/webhook/retell",
                json=payload
            )
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            print("   ✅ Processes call_started event")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        # Test 5: POST with unknown event type
        print("\n5. Testing POST /api/v1/webhook/retell with unknown event...")
        try:
            payload = {
                "event": "unknown_event",
                "data": {"test": "data"}
            }
            response = await client.post(
                f"{base_url}/api/v1/webhook/retell",
                json=payload
            )
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            print("   ✅ Handles unknown events correctly")
        except Exception as e:
            print(f"   ❌ Error: {e}")

    print("\n" + "=" * 60)
    print("Webhook Tests Complete")
    print("=" * 60)
    print("\n💡 Tips:")
    print("   - Webhook URL for Retell: http://localhost:8000/api/v1/webhook/retell")
    print("   - For production, replace localhost with your public URL")
    print("   - Use ngrok or similar tool for local testing with Retell")
    print("   - Example: ngrok http 8000")

if __name__ == "__main__":
    asyncio.run(test_webhook_endpoint())
