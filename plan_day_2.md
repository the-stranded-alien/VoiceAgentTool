How to Test the Real-Time Voice Conversation System
Great question! Here's a comprehensive testing guide for what we've built:

1. Quick WebSocket Test (Already Passing ✅)
We already verified the WebSocket works with the test script:


cd /Users/sahilgupta/Repositories/VoiceAgentTool/backend
source .venv/bin/activate
python test_websocket_client.py
This simulates Retell's messages and confirms:

✅ WebSocket connects
✅ Opening greeting generated
✅ Normal conversation responses work
✅ Emergency detection activates instantly
2. Test with Retell Web Call (Recommended - No Phone Required)
Since you're likely not in the USA, use Retell Web Calls to test in your browser:

Step 1: Configure Agent to Use Your WebSocket
First, you need to expose your local WebSocket to the internet (Retell needs to reach it):

Option A: Using ngrok (easiest)


# Install ngrok if you don't have it
brew install ngrok  # macOS

# Expose your backend
ngrok http 8000

# You'll get a URL like: https://abc123.ngrok.io
Option B: Using Cloudflare Tunnel


cloudflared tunnel --url http://localhost:8000
Step 2: Update Agent Configuration
In your frontend or via API, create/update an agent with:

custom_llm_websocket_url: wss://your-ngrok-url/ws/llm (note: wss:// for secure WebSocket)
scenario_type: check_in
driver info in metadata
Step 3: Trigger a Web Call
From your frontend's "Trigger Call" page:

Enter driver name: "Mike"
Phone number: (not used for web calls)
Load number: "7891-B"
Click "Start Test Call" but choose Web Call option
Or via API:


curl -X POST http://localhost:8000/api/v1/calls/{call_id}/initiate \
  -H "Content-Type: application/json" \
  -d '{"use_web_call": true}'
This returns an access_token you can use with Retell's Web SDK in your browser.

Step 4: Test in Browser
You can test the web call using Retell's test interface or implement the Retell Web SDK in your frontend.

3. Monitor the Conversation
While testing, watch the backend logs:


# In a separate terminal
tail -f /tmp/claude/-Users-sahilgupta-Repositories-VoiceAgentTool/tasks/b6e643f.output
You'll see:

WebSocket connection established
Call details received
User utterances
Agent responses
Emergency detection (if triggered)
4. Test Scenarios
Scenario A: Normal Check-In
Say: "I'm driving on I-10 near Indio"
Expect: Agent asks for ETA or delays

Say: "Should be there around 8 AM tomorrow"
Expect: Agent asks about any issues/delays

Say: "No issues, all good"
Expect: Agent thanks you and ends call

Scenario B: Emergency Protocol
Start normally: "I'm driving to Phoenix"
Then say: "Wait, I just had a blowout!"
Expect: Agent immediately says "I understand, let me help you. Is everyone safe?"

Say: "Yes, we're all safe"
Expect: Agent asks for location

Say: "I-15 North, mile marker 123"
Expect: Agent asks if load is secure

Say: "Yes, truck is on the shoulder, load is fine"
Expect: Agent says "I'm connecting you to a human dispatcher now"

Scenario C: Uncooperative Driver
Say: "Yeah" (one word)
Expect: Agent asks more specifically

Say: "Fine" (one word again)
Expect: After 3-5 attempts, agent says "I'll let you go for now..."

5. Verify Data Extraction
After the call ends, check the call details:


# Get call by ID
curl http://localhost:8000/api/v1/calls/{call_id}
Look for:

structured_data field containing extracted information
call_outcome classification
raw_transcript with full conversation
6. Production Testing Checklist
Before going live:

 Test normal check-in flow (driving scenario)
 Test normal check-in flow (arrived scenario)
 Test emergency mid-call switch
 Test uncooperative driver handling
 Test noisy environment (low confidence)
 Verify structured data extraction is accurate
 Verify webhook receives call_ended event
 Verify dashboard stats update correctly
7. Quick Debug Commands

# Check if WebSocket endpoint is accessible
curl -i -N -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" \
  -H "Sec-WebSocket-Key: test" \
  http://localhost:8000/ws/llm

# Check active contexts (via Python)
python -c "
from app.services.llm.context import get_context_manager
cm = get_context_manager()
print('Active contexts:', cm.get_all_active_contexts())
"

# View recent calls
curl http://localhost:8000/api/v1/calls?limit=5
What's Next?
The core voice engine is complete! The remaining work from the plan is:

Phase 2: Frontend structured data display (show extracted fields in UI)
Phase 3: Emergency notifications (email/SMS alerts)
Phase 4: Edge case refinements
Phase 5: Voice setting optimization
Phase 6: End-to-end testing