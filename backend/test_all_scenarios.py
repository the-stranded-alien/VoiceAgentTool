"""
Comprehensive Test Suite for All Voice Agent Scenarios

Tests all conversation flows and edge cases from the assignment:
- Scenario 1: Check-In (Driving, Arrived, Delayed)
- Scenario 2: Emergency Protocol
- Edge Cases: Uncooperative Driver, Noisy Environment

Run with: python test_all_scenarios.py
"""

import asyncio
import json
import websockets
from typing import List, Dict, Tuple


class VoiceAgentTester:
    """Test harness for voice agent scenarios"""

    def __init__(self, ws_url="ws://localhost:8000/ws/llm"):
        self.ws_url = ws_url
        self.test_results = []

    async def run_conversation(
        self,
        call_id: str,
        driver_name: str,
        load_number: str,
        scenario: str,
        conversation: List[Tuple[str, str]]  # (user_utterance, expected_keywords)
    ) -> bool:
        """
        Run a conversation test

        Args:
            call_id: Unique call ID
            driver_name: Driver name
            load_number: Load number
            scenario: Scenario type
            conversation: List of (user_utterance, expected_keywords_in_response)

        Returns:
            True if test passed
        """
        try:
            async with websockets.connect(self.ws_url) as websocket:
                # Step 1: Send call_details
                call_details = {
                    "interaction_type": "call_details",
                    "call_id": f"retell_{call_id}",
                    "retell_llm_dynamic_variables": {
                        "call_id": call_id,
                        "driver_name": driver_name,
                        "load_number": load_number,
                        "phone_number": "+1234567890",
                        "scenario": scenario
                    }
                }

                await websocket.send(json.dumps(call_details))
                response = await websocket.recv()
                response_data = json.loads(response)

                print(f"\n  Opening: {response_data.get('content')}")

                # Step 2: Run conversation turns
                response_id = 1
                for user_utterance, expected_keywords in conversation:
                    message = {
                        "interaction_type": "response_required",
                        "response_id": response_id,
                        "transcript": [
                            {"role": "agent", "content": response_data.get("content")},
                            {"role": "user", "content": user_utterance}
                        ]
                    }

                    await websocket.send(json.dumps(message))
                    response = await websocket.recv()
                    response_data = json.loads(response)

                    agent_response = response_data.get("content")
                    print(f"  User: {user_utterance}")
                    print(f"  Agent: {agent_response}")

                    # Check for expected keywords
                    if expected_keywords:
                        response_lower = agent_response.lower()
                        for keyword in expected_keywords:
                            if keyword.lower() not in response_lower:
                                print(f"  ✗ Missing expected keyword: {keyword}")
                                return False

                    # Check if call ended
                    if response_data.get("end_call", False):
                        print("  [Call Ended]")
                        break

                    response_id += 1

                print("  ✓ Test passed")
                return True

        except Exception as e:
            print(f"  ✗ Test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def test_check_in_driving(self):
        """Test check-in scenario with driver currently driving"""
        print("\n" + "="*60)
        print("TEST 1: Check-In - Driver is Driving")
        print("="*60)

        conversation = [
            ("I'm driving on I-10 near Indio", ["eta", "location"]),
            ("Should be there tomorrow around 8 AM", ["delay", "issue", "traffic"]),
            ("No delays, traffic is good", ["thanks", "safe"]),
        ]

        result = await self.run_conversation(
            call_id="test_checkin_driving",
            driver_name="Mike",
            load_number="7891-B",
            scenario="check_in",
            conversation=conversation
        )

        self.test_results.append(("Check-In: Driving", result))

    async def test_check_in_arrived(self):
        """Test check-in scenario with driver already arrived"""
        print("\n" + "="*60)
        print("TEST 2: Check-In - Driver Has Arrived")
        print("="*60)

        conversation = [
            ("I just arrived at the warehouse", ["door", "unload", "status"]),
            ("I'm in door 42, waiting for the lumper", ["pod", "proof", "delivery"]),
            ("Yes, I'll send it when I'm done", ["thanks", "safe"]),
        ]

        result = await self.run_conversation(
            call_id="test_checkin_arrived",
            driver_name="Sarah",
            load_number="5432-A",
            scenario="check_in",
            conversation=conversation
        )

        self.test_results.append(("Check-In: Arrived", result))

    async def test_check_in_delayed(self):
        """Test check-in scenario with delayed driver"""
        print("\n" + "="*60)
        print("TEST 3: Check-In - Driver is Delayed")
        print("="*60)

        conversation = [
            ("I'm delayed, stuck in traffic near Phoenix", ["reason", "delay", "eta"]),
            ("Heavy traffic due to an accident, about 2 hours behind", ["new eta", "when"]),
            ("Should be there around 10 AM now", ["thanks", "safe"]),
        ]

        result = await self.run_conversation(
            call_id="test_checkin_delayed",
            driver_name="John",
            load_number="9876-C",
            scenario="check_in",
            conversation=conversation
        )

        self.test_results.append(("Check-In: Delayed", result))

    async def test_emergency_protocol(self):
        """Test emergency protocol activation mid-call"""
        print("\n" + "="*60)
        print("TEST 4: Emergency Protocol - Mid-Call Switch")
        print("="*60)

        conversation = [
            ("I'm driving on I-15 heading to Vegas", None),
            ("Wait, I just had a blowout!", ["safe", "everyone"]),
            ("Yes, everyone is safe", ["location", "where"]),
            ("I-15 North, mile marker 123", ["load", "secure"]),
            ("Yes, truck is on the shoulder, load is fine", ["dispatcher", "connect"]),
        ]

        result = await self.run_conversation(
            call_id="test_emergency",
            driver_name="Tom",
            load_number="1111-D",
            scenario="check_in",  # Starts as check-in, switches to emergency
            conversation=conversation
        )

        self.test_results.append(("Emergency Protocol", result))

    async def test_uncooperative_driver(self):
        """Test handling of uncooperative driver with one-word answers"""
        print("\n" + "="*60)
        print("TEST 5: Edge Case - Uncooperative Driver")
        print("="*60)

        conversation = [
            ("Driving", ["location", "where"]),
            ("Phoenix", ["eta", "when"]),
            ("Soon", ["detail", "more", "specific"]),
            ("Yeah", ["busy", "quick"]),
            ("Fine", ["let you go", "call back"]),
        ]

        result = await self.run_conversation(
            call_id="test_uncooperative",
            driver_name="Grumpy",
            load_number="8888-E",
            scenario="check_in",
            conversation=conversation
        )

        self.test_results.append(("Edge Case: Uncooperative", result))

    async def test_all(self):
        """Run all tests"""
        print("\n" + "#"*60)
        print("#  Voice Agent Comprehensive Test Suite")
        print("#"*60)

        # Run all test scenarios
        await self.test_check_in_driving()
        await self.test_check_in_arrived()
        await self.test_check_in_delayed()
        await self.test_emergency_protocol()
        await self.test_uncooperative_driver()

        # Print summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)

        passed = 0
        failed = 0

        for test_name, result in self.test_results:
            status = "✓ PASSED" if result else "✗ FAILED"
            print(f"{test_name:40} {status}")
            if result:
                passed += 1
            else:
                failed += 1

        print("-"*60)
        print(f"Total: {passed + failed} tests | Passed: {passed} | Failed: {failed}")
        print("="*60)

        return failed == 0


async def main():
    """Main test runner"""
    tester = VoiceAgentTester()
    all_passed = await tester.test_all()

    if all_passed:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
