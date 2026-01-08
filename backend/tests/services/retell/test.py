import asyncio
from app.services.retell.client import get_retell_client
from app.services.retell.agent import get_retell_agent_service
from app.services.retell.call import get_retell_call_service
from app.services.call_service import CallService
from app.database import get_supabase
from app.models.call import CallCreate

async def test_connection():
    """Test Retell SDK connection"""
    print("=" * 60)
    print("Testing Retell SDK Connection")
    print("=" * 60)
    
    try:
        client = get_retell_client()
        
        # Test: List agents
        print("\n1. Listing agents...")
        agents = client.list_agents()
        print(f"✅ Found {len(agents)} agents")
        for agent in agents[:3]:
            print(f"   - {agent.agent_name} (ID: {agent.agent_id})")
        
        # Test: List phone numbers
        print("\n2. Listing phone numbers...")
        numbers = client.list_phone_numbers()
        print(f"✅ Found {len(numbers)} phone numbers")
        for number in numbers:
            print(f"   - {number.phone_number}")
        
        # Test: List calls
        print("\n3. Listing recent calls...")
        calls = client.list_calls(limit=5)
        print(f"✅ Found {len(calls)} recent calls")
        
        print("\n✅ All connection tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Connection test failed: {str(e)}")
        return False

async def test_agent_creation():
    """Test agent creation using SDK"""
    print("\n" + "=" * 60)
    print("Testing Agent Creation")
    print("=" * 60)
    
    try:
        agent_service = get_retell_agent_service()
        
        # Create test agent
        print("\n1. Creating test agent...")
        test_config = {
            "name": "SDK Test Agent",
            "scenario_type": "check_in",
            "voice_settings": {
                "voice_id": "11labs-Adrian",
                "response_delay": 0.8,
                "interruption_sensitivity": 0.7,
                "backchannel": {
                    "enabled": True,
                    "frequency": "medium"
                },
                "filler_words": {
                    "enabled": True
                }
            }
        }
        
        agent_id = agent_service.create_agent_from_config(test_config)
        print(f"✅ Created agent: {agent_id}")
        
        # Get agent details
        print("\n2. Retrieving agent details...")
        agent = agent_service.get_agent(agent_id)
        print(f"✅ Retrieved: {agent.agent_name}")
        print(f"   Voice: {agent.voice_id}")
        print(f"   Responsiveness: {agent.responsiveness}")
        
        # Clean up
        print("\n3. Cleaning up test agent...")
        success = agent_service.delete_agent(agent_id)
        if success:
            print("✅ Test agent deleted")
        
        print("\n✅ All agent tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Agent test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_web_call_creation():
    """Test web call creation"""
    print("\n" + "=" * 60)
    print("Testing Web Call Creation")
    print("=" * 60)

    call_id = None
    agent_id = None

    try:
        # Create a test agent
        agent_service = get_retell_agent_service()
        test_config = {
            "name": "Web Call Test Agent",
            "scenario_type": "check_in",
            "voice_settings": {}
        }

        print("\n1. Creating test agent for web call...")
        agent_id = agent_service.create_agent_from_config(test_config)
        print(f"✅ Agent created: {agent_id}")

        # Get an existing agent config from database
        print("\n2. Getting agent config from database...")
        supabase = get_supabase()

        agent_config_response = supabase.table("agent_configs").select("id").limit(1).execute()
        if not agent_config_response.data:
            print("⚠️  No agent configs found in database, skipping database integration")
            print("   Testing SDK-only web call creation...")

            # Test SDK-only functionality
            client = get_retell_client()
            response = client.create_web_call(
                agent_id=agent_id,
                metadata={
                    "driver_name": "Test Driver",
                    "load_number": "TEST-001",
                    "test": "true"
                },
                retell_llm_dynamic_variables={
                    "driver_name": "Test Driver",
                    "load_number": "TEST-001"
                }
            )

            print(f"✅ Web call created (SDK only)!")
            print(f"   Retell Call ID: {response.call_id}")
            print(f"   Access Token: {response.access_token[:20]}...")
            print(f"   Call Status: {response.call_status}")

        else:
            agent_config_id = agent_config_response.data[0]["id"]
            print(f"✅ Found agent config: {agent_config_id}")

            # Create a call record in the database
            print("\n3. Creating call record in database...")
            call_service = CallService(supabase)

            call_create = CallCreate(
                agent_config_id=agent_config_id,
                driver_name="Test Driver",
                driver_phone="+1234567890",
                load_number="TEST-001"
            )

            call = await call_service.create_call(call_create)
            call_id = call.id
            print(f"✅ Call record created: {call_id}")

            # Create web call using the call service
            print("\n4. Creating web call with Retell SDK...")
            retell_call_service = get_retell_call_service()

            result = await retell_call_service.create_web_call(
                call_id=call_id,
                retell_agent_id=agent_id,
                driver_name="Test Driver",
                load_number="TEST-001"
            )

            print(f"✅ Web call created!")
            print(f"   Internal Call ID: {result['call_id']}")
            print(f"   Retell Call ID: {result['retell_call_id']}")
            print(f"   Access Token: {result['access_token'][:20]}...")

        print("\n✅ Web call test passed!")
        print("\nNote: To test the actual call, you would use the Retell Web SDK")
        print("with the access_token in a browser.")

        return True

    except Exception as e:
        print(f"\n❌ Web call test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Clean up
        print("\n5. Cleaning up...")
        try:
            if agent_id:
                agent_service.delete_agent(agent_id)
                print("✅ Test agent deleted")
            # Note: We're leaving the call record in the database for debugging
            # In production, you might want to delete it or mark it as test data
        except Exception as cleanup_error:
            print(f"⚠️  Cleanup warning: {cleanup_error}")

async def main():
    """Run all tests"""
    print("\n🚀 Starting Retell SDK Tests\n")
    
    results = []
    
    # Run tests
    results.append(await test_connection())
    results.append(await test_agent_creation())
    results.append(await test_web_call_creation())
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)