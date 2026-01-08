# Complete Voice Agent Assignment Requirements

## Executive Summary

Based on comprehensive codebase exploration, the application has strong foundational infrastructure but is **missing critical real-time voice conversation capabilities** required by the assignment. The main gap is the **Retell Custom LLM WebSocket integration** for dynamic conversation control during calls.

## Current State Assessment

### ✅ What's Implemented (Strong Foundation)

1. **Agent Configuration** - Full CRUD, voice settings, scenario types
2. **Call Management** - Phone & web calls, status tracking, event logging
3. **Webhook Handling** - Call lifecycle events (started, ended, analyzed)
4. **Post-Call Processing** - Transcript extraction, structured data extraction, call outcome classification
5. **LLM Integration** - Claude-based extraction with schemas for check-in and emergency scenarios
6. **Frontend UI** - Agent config, call triggering, dashboard, history pages
7. **Database** - Supabase integration with complete schema

### ❌ Critical Missing Components

1. **Retell Custom LLM WebSocket** - No real-time conversation engine
2. **Scenario-Specific System Prompts** - No pre-built conversation templates
3. **Mid-Call Emergency Detection** - Only detects emergencies post-call
4. **Dynamic Conversation Flow** - No real-time context switching
5. **Structured Data Display** - Frontend doesn't show extracted fields
6. **Emergency Escalation Action** - No actual escalation mechanism

---

## Implementation Plan - Prioritized by Assignment Requirements

## Phase 1: Enable Real-Time Voice Conversations (CRITICAL)

### 1.1 Implement Retell Custom LLM WebSocket Endpoint

**Problem**: Retell needs a WebSocket endpoint to request LLM responses during the call. Currently, agents are configured with `custom_llm_websocket_url` but no WebSocket server exists.

**Files to Create/Modify**:
- **NEW**: `backend/app/api/websocket.py` - WebSocket endpoint handler
- **NEW**: `backend/app/services/llm/realtime.py` - Real-time LLM response generator
- **MODIFY**: `backend/app/main.py` - Mount WebSocket routes

**Implementation Details**:

```python
# WebSocket Message Flow:
# 1. Retell sends: {"interaction_type": "response_required", "transcript": [...], "context": {...}}
# 2. Backend generates response using Claude
# 3. Backend responds: {"response_type": "response", "content": "Agent's reply", "end_call": false}
```

**Key Features**:
- Parse incoming Retell messages (response_required, reminder_required, call_details)
- Maintain conversation context (multi-turn memory)
- Generate dynamic responses based on:
  - Current scenario (check-in vs emergency)
  - Driver information (name, load number)
  - Conversation history
  - Emergency triggers
- Handle scenario switching (normal → emergency escalation)
- Support end-call decision making

**Critical Logic**:
```python
# Emergency detection mid-call:
if detect_emergency_keywords(transcript):
    switch_to_emergency_protocol()
    return emergency_response()
```

### 1.2 Create Scenario-Specific System Prompts

**Files to Modify**:
- **MODIFY**: `backend/app/services/llm/prompts.py` - Add complete conversation templates

**Templates Needed**:

1. **CHECK_IN_SYSTEM_PROMPT** - For Scenario 1
   - Opening: "Hi {driver_name}, this is Dispatch with a check call on load {load_number}..."
   - Dynamic questioning based on driver response
   - Information gathering: status, location, ETA, delays, unloading, POD
   - Natural conversation flow with follow-ups
   - Graceful closing

2. **EMERGENCY_SYSTEM_PROMPT** - For Scenario 2
   - Emergency trigger phrases: "accident", "breakdown", "blowout", "medical", etc.
   - Immediate protocol switch
   - Critical information gathering: safety, injuries, location, load security
   - Escalation statement: "I'm connecting you to a human dispatcher now"
   - Calm, professional tone

3. **EDGE_CASE_PROMPTS**:
   - Uncooperative driver handling
   - Noisy environment / speech recognition errors
   - Conflicting location data handling

**Integration**:
- Agent model already has `system_prompt` field
- Add `prompt_template_type` field to agent model (check_in, emergency, custom)
- Auto-populate prompt based on scenario_type

### 1.3 Build Conversation Context Manager

**Files to Create**:
- **NEW**: `backend/app/services/llm/context.py` - Conversation state management

**Functionality**:
- Track conversation turns (user utterances + agent responses)
- Store extracted information as conversation progresses
- Detect completion criteria (all required fields collected)
- Handle scenario transitions (check-in → emergency)
- Provide context to LLM for coherent multi-turn responses

**Data Structure**:
```python
class ConversationContext:
    call_id: str
    scenario: str  # check_in, emergency
    driver_info: dict  # name, load_number
    conversation_history: List[Turn]
    extracted_data: dict  # incremental extraction
    is_emergency: bool
    completion_status: dict  # which fields are collected
```

---

## Phase 2: Complete Scenario 1 - End-to-End Driver Check-In

### 2.1 Implement Dynamic Conversation Flow

**Goal**: Agent asks open-ended "Can you give me an update?" and pivots based on response.

**Implementation**:
- WebSocket handler detects driver status from initial response
- Branches conversation:
  - If "driving" → ask location, ETA, delays
  - If "arrived" → ask unloading status, door number
  - If "delayed" → ask delay reason, new ETA
- Follow-up questions based on gaps in extracted data
- Natural transitions between topics

**Files to Modify**:
- `backend/app/services/llm/realtime.py` - Add conversation flow logic
- `backend/app/services/llm/prompts.py` - Add follow-up question templates

### 2.2 Enhance Structured Data Extraction

**Current State**: CHECK_IN_SCHEMA exists in `schemas.py`

**Enhancements Needed**:
- Real-time incremental extraction (update after each turn, not just post-call)
- Validation logic for required vs optional fields
- Confidence scoring for extracted values
- Handling ambiguous responses ("maybe", "I think", "around")

**Files to Modify**:
- `backend/app/services/llm/extractor.py` - Add incremental extraction
- `backend/app/services/llm/schemas.py` - Add validation rules

### 2.3 Frontend Display for Check-In Data

**Goal**: Show structured key-value pairs after call completion

**Files to Modify**:
- `frontend/src/pages/CallDetailsPage.tsx` - Add structured data display section
- **NEW**: `frontend/src/components/StructuredDataView.tsx` - Reusable component

**UI Design**:
```
Call Outcome: In-Transit Update
Driver Status: Driving
Current Location: I-10 near Indio, CA
ETA: Tomorrow, 8:00 AM
Delay Reason: Heavy Traffic
POD Reminder Acknowledged: Yes
```

---

## Phase 3: Complete Scenario 2 - Dynamic Emergency Protocol

### 3.1 Implement Mid-Call Emergency Detection

**Problem**: Currently emergency detection only happens post-call via transcript analysis

**Solution**: Real-time keyword monitoring in WebSocket handler

**Files to Modify**:
- `backend/app/services/llm/realtime.py` - Add emergency trigger detection
- `backend/app/services/llm/prompts.py` - Add emergency protocol prompts

**Emergency Triggers**:
```python
EMERGENCY_KEYWORDS = [
    "accident", "crash", "blowout", "breakdown",
    "medical", "emergency", "injured", "hurt",
    "pulling over", "can't drive", "need help"
]
```

**Detection Logic**:
```python
# In WebSocket message handler:
if detect_emergency_in_transcript(latest_transcript):
    context.switch_to_emergency()
    return generate_emergency_response()
```

### 3.2 Build Emergency Escalation Flow

**Goal**: Agent gathers critical info then states it's connecting to human dispatcher

**Conversation Flow**:
1. Detect emergency trigger
2. Immediate acknowledgment: "I understand, let me help you"
3. Safety check: "Is everyone safe?"
4. Gather critical info:
   - Emergency type
   - Injuries
   - Location
   - Load security
5. Escalation statement: "I'm connecting you to a human dispatcher now"
6. End call with escalation status

**Files to Modify**:
- `backend/app/services/llm/conversation.py` - Add emergency conversation generator
- `backend/app/models/call.py` - Ensure ESCALATED status is used

### 3.3 Emergency Notification System

**Goal**: Alert human dispatchers when emergency is detected

**Files to Create**:
- **NEW**: `backend/app/services/notifications.py` - Email/SMS alerts

**Implementation**:
- Trigger when call status → ESCALATED
- Send notification with:
  - Driver name, phone
  - Emergency type
  - Location
  - Safety status
  - Link to call details

**Integration Point**:
- `backend/app/api/webhooks.py` - Add notification trigger in call_ended handler

### 3.4 Frontend Emergency UI

**Files to Modify**:
- `frontend/src/pages/CallDetailsPage.tsx` - Add emergency banner
- `frontend/src/components/EmergencyAlert.tsx` - Visual indicator

**UI Design**:
```
🚨 EMERGENCY ESCALATION
Emergency Type: Breakdown
Safety Status: Driver confirmed everyone is safe
Location: I-15 North, Mile Marker 123
Load Secure: Yes
Status: Connected to Human Dispatcher
```

---

## Phase 4: Task B - Dynamic Response Handling

### 4.1 Uncooperative Driver Handling

**Implementation**:
- Track one-word responses count
- After 3 attempts, probe: "I need a bit more detail to help you..."
- After 5+ attempts: "I'll let you go for now. Please call back when you have more time."
- Set call_outcome: "Unresponsive Driver"

**Files to Modify**:
- `backend/app/services/llm/realtime.py` - Add response quality tracking

### 4.2 Noisy Environment Handling

**Implementation**:
- Detect low-confidence transcriptions (Retell provides confidence scores)
- Ask clarification: "I didn't quite catch that, could you repeat?"
- Limit to 3 repetitions per topic
- If still unclear, escalate: "I'm having trouble hearing you. Let me connect you to dispatch."

**Files to Modify**:
- `backend/app/services/llm/realtime.py` - Add transcription confidence handling

### 4.3 Conflicting Driver Handling

**Scenario**: Driver says "I'm in Phoenix" but GPS shows Barstow

**Implementation**:
- Non-confrontational approach: "Thanks for the update. Our system shows you near Barstow - just wanted to confirm which is correct?"
- Accept driver's answer without argument
- Flag discrepancy in structured data

**Files to Modify**:
- `backend/app/services/llm/prompts.py` - Add conflict resolution prompts
- `backend/app/services/llm/schemas.py` - Add `location_discrepancy` field

---

## Phase 5: Voice Configuration Best Practices (Task A)

### 5.1 Optimize Retell Voice Settings

**Current State**: Agent model has fields but may not use optimal values

**Recommended Settings**:
```python
# For human-like experience:
interruption_sensitivity = 1.0  # Allow natural interruptions
enable_backchannel = True  # "uh-huh", "I see"
ambient_sound = "office"  # Sounds like real dispatch
speaking_rate = 1.0  # Natural pace
response_delay = 100  # ms, slight pause feels natural
```

**Files to Modify**:
- `backend/app/services/retell/agent.py` - Update default values
- Frontend agent config form - Add descriptions/recommendations

### 5.2 Test Voice Settings

**Testing Plan**:
- Create test agents with different configurations
- Compare:
  - With/without backchannel
  - Different interruption sensitivities
  - Various speaking rates
- Document optimal settings in README

---

## Phase 6: Testing & Polish

### 6.1 End-to-End Testing

**Test Cases**:

1. **Check-In - Driving**
   - Trigger call with driver info
   - Simulate "I'm driving on I-10 near Indio"
   - Verify agent asks for ETA, delays, POD
   - Confirm structured data extraction

2. **Check-In - Arrived**
   - Simulate "I just arrived at the warehouse"
   - Verify agent asks about unloading, door number
   - Confirm data extraction

3. **Emergency - Mid-Call Switch**
   - Start normal check-in
   - Interrupt with "I just had a blowout!"
   - Verify protocol switch
   - Confirm emergency data extraction
   - Verify escalation status

4. **Edge Case - Uncooperative**
   - Give one-word answers
   - Verify probing questions
   - Confirm graceful call end

5. **Edge Case - Noisy**
   - Simulate garbled speech
   - Verify clarification requests
   - Confirm escalation after retries

6. **Web Call Testing**
   - Test with Retell Web SDK in browser
   - Verify WebSocket connection
   - Confirm real-time responses

**Files to Create**:
- `backend/tests/test_websocket.py` - WebSocket unit tests
- `backend/tests/test_scenarios.py` - Scenario integration tests

### 6.2 Webhook Security

**Implementation**:
- Validate Retell webhook signature
- Use `retell_webhook_secret_key` from config

**Files to Modify**:
- `backend/app/api/webhooks.py` - Add signature verification

### 6.3 Error Handling & Logging

**Enhancements**:
- Graceful LLM failures (use fallback responses)
- Database failure handling (retry logic)
- WebSocket disconnection recovery
- Comprehensive logging for debugging

**Files to Modify**:
- All service files - Add try/catch with logging
- `backend/app/services/llm/realtime.py` - Fallback responses

---

## Critical Files by Component

### Backend - Core Voice Engine
- `backend/app/api/websocket.py` - **NEW** WebSocket endpoint
- `backend/app/services/llm/realtime.py` - **NEW** Real-time LLM handler
- `backend/app/services/llm/context.py` - **NEW** Conversation state
- `backend/app/services/llm/prompts.py` - **MODIFY** Add scenario templates
- `backend/app/services/llm/extractor.py` - **MODIFY** Incremental extraction
- `backend/app/services/retell/agent.py` - **MODIFY** Optimal voice settings

### Backend - Webhooks & Events
- `backend/app/api/webhooks.py` - **MODIFY** Add signature verification, notifications
- `backend/app/services/notifications.py` - **NEW** Emergency alerts

### Frontend - Data Display
- `frontend/src/pages/CallDetailsPage.tsx` - **MODIFY** Show structured data
- `frontend/src/components/StructuredDataView.tsx` - **NEW** Data display component
- `frontend/src/components/EmergencyAlert.tsx` - **NEW** Emergency banner

### Configuration & Setup
- `backend/app/main.py` - **MODIFY** Mount WebSocket routes
- `backend/.env` - Ensure all Retell credentials present

---

## Verification Steps

### After Implementation:

1. **Test WebSocket Connectivity**
```bash
# Start backend
cd backend && source .venv/bin/activate && uvicorn app.main:app --reload

# Test WebSocket endpoint exists
curl http://localhost:8000/ws/llm
```

2. **Test Check-In Scenario**
- Create check-in agent via UI
- Trigger test call (use web call if outside USA)
- Monitor backend logs for WebSocket messages
- Verify conversation flow
- Check structured data extraction in UI

3. **Test Emergency Scenario**
- Create emergency agent via UI
- Trigger test call
- Interrupt with emergency phrase
- Verify protocol switch
- Confirm escalation status
- Check emergency notification sent

4. **Test Edge Cases**
- Trigger call with uncooperative responses
- Verify graceful handling
- Test noisy environment simulation
- Verify clarification flow

5. **Review Call History**
- Verify all calls are logged
- Check structured data is displayed
- Confirm transcripts are saved
- Verify dashboard stats are accurate

---

## Timeline Estimate

- **Phase 1** (WebSocket + Prompts): 8-10 hours
- **Phase 2** (Check-In Scenario): 4-6 hours
- **Phase 3** (Emergency Scenario): 4-6 hours
- **Phase 4** (Edge Cases): 3-4 hours
- **Phase 5** (Voice Optimization): 2-3 hours
- **Phase 6** (Testing & Polish): 4-5 hours

**Total**: ~25-34 hours of focused development

---

## Success Criteria

✅ Agent can have natural, multi-turn conversation during calls
✅ Check-in scenario dynamically pivots based on driver status
✅ Emergency protocol immediately activates on trigger phrases
✅ All structured data fields are extracted correctly
✅ Frontend displays structured data in clean key-value format
✅ Edge cases are handled gracefully
✅ Web calls work for testing (important for non-USA developers)
✅ Code follows existing patterns and quality standards
✅ README documents all features and setup instructions
Perfect! I've created a comprehensive plan. Now let me call ExitPlanMode to present this plan for approval.

Claude’s Plan
Complete Voice Agent Assignment Requirements
Executive Summary
Based on comprehensive codebase exploration, the application has strong foundational infrastructure but is missing critical real-time voice conversation capabilities required by the assignment. The main gap is the Retell Custom LLM WebSocket integration for dynamic conversation control during calls.

Current State Assessment
✅ What's Implemented (Strong Foundation)
Agent Configuration - Full CRUD, voice settings, scenario types
Call Management - Phone & web calls, status tracking, event logging
Webhook Handling - Call lifecycle events (started, ended, analyzed)
Post-Call Processing - Transcript extraction, structured data extraction, call outcome classification
LLM Integration - Claude-based extraction with schemas for check-in and emergency scenarios
Frontend UI - Agent config, call triggering, dashboard, history pages
Database - Supabase integration with complete schema
❌ Critical Missing Components
Retell Custom LLM WebSocket - No real-time conversation engine
Scenario-Specific System Prompts - No pre-built conversation templates
Mid-Call Emergency Detection - Only detects emergencies post-call
Dynamic Conversation Flow - No real-time context switching
Structured Data Display - Frontend doesn't show extracted fields
Emergency Escalation Action - No actual escalation mechanism
Implementation Plan - Prioritized by Assignment Requirements
Phase 1: Enable Real-Time Voice Conversations (CRITICAL)
1.1 Implement Retell Custom LLM WebSocket Endpoint
Problem: Retell needs a WebSocket endpoint to request LLM responses during the call. Currently, agents are configured with custom_llm_websocket_url but no WebSocket server exists.

Files to Create/Modify:

NEW: backend/app/api/websocket.py - WebSocket endpoint handler
NEW: backend/app/services/llm/realtime.py - Real-time LLM response generator
MODIFY: backend/app/main.py - Mount WebSocket routes
Implementation Details:


# WebSocket Message Flow:
# 1. Retell sends: {"interaction_type": "response_required", "transcript": [...], "context": {...}}
# 2. Backend generates response using Claude
# 3. Backend responds: {"response_type": "response", "content": "Agent's reply", "end_call": false}
Key Features:

Parse incoming Retell messages (response_required, reminder_required, call_details)
Maintain conversation context (multi-turn memory)
Generate dynamic responses based on:
Current scenario (check-in vs emergency)
Driver information (name, load number)
Conversation history
Emergency triggers
Handle scenario switching (normal → emergency escalation)
Support end-call decision making
Critical Logic:


# Emergency detection mid-call:
if detect_emergency_keywords(transcript):
    switch_to_emergency_protocol()
    return emergency_response()
1.2 Create Scenario-Specific System Prompts
Files to Modify:

MODIFY: backend/app/services/llm/prompts.py - Add complete conversation templates
Templates Needed:

CHECK_IN_SYSTEM_PROMPT - For Scenario 1

Opening: "Hi {driver_name}, this is Dispatch with a check call on load {load_number}..."
Dynamic questioning based on driver response
Information gathering: status, location, ETA, delays, unloading, POD
Natural conversation flow with follow-ups
Graceful closing
EMERGENCY_SYSTEM_PROMPT - For Scenario 2

Emergency trigger phrases: "accident", "breakdown", "blowout", "medical", etc.
Immediate protocol switch
Critical information gathering: safety, injuries, location, load security
Escalation statement: "I'm connecting you to a human dispatcher now"
Calm, professional tone
EDGE_CASE_PROMPTS:

Uncooperative driver handling
Noisy environment / speech recognition errors
Conflicting location data handling
Integration:

Agent model already has system_prompt field
Add prompt_template_type field to agent model (check_in, emergency, custom)
Auto-populate prompt based on scenario_type
1.3 Build Conversation Context Manager
Files to Create:

NEW: backend/app/services/llm/context.py - Conversation state management
Functionality:

Track conversation turns (user utterances + agent responses)
Store extracted information as conversation progresses
Detect completion criteria (all required fields collected)
Handle scenario transitions (check-in → emergency)
Provide context to LLM for coherent multi-turn responses
Data Structure:


class ConversationContext:
    call_id: str
    scenario: str  # check_in, emergency
    driver_info: dict  # name, load_number
    conversation_history: List[Turn]
    extracted_data: dict  # incremental extraction
    is_emergency: bool
    completion_status: dict  # which fields are collected
Phase 2: Complete Scenario 1 - End-to-End Driver Check-In
2.1 Implement Dynamic Conversation Flow
Goal: Agent asks open-ended "Can you give me an update?" and pivots based on response.

Implementation:

WebSocket handler detects driver status from initial response
Branches conversation:
If "driving" → ask location, ETA, delays
If "arrived" → ask unloading status, door number
If "delayed" → ask delay reason, new ETA
Follow-up questions based on gaps in extracted data
Natural transitions between topics
Files to Modify:

backend/app/services/llm/realtime.py - Add conversation flow logic
backend/app/services/llm/prompts.py - Add follow-up question templates
2.2 Enhance Structured Data Extraction
Current State: CHECK_IN_SCHEMA exists in schemas.py

Enhancements Needed:

Real-time incremental extraction (update after each turn, not just post-call)
Validation logic for required vs optional fields
Confidence scoring for extracted values
Handling ambiguous responses ("maybe", "I think", "around")
Files to Modify:

backend/app/services/llm/extractor.py - Add incremental extraction
backend/app/services/llm/schemas.py - Add validation rules
2.3 Frontend Display for Check-In Data
Goal: Show structured key-value pairs after call completion

Files to Modify:

frontend/src/pages/CallDetailsPage.tsx - Add structured data display section
NEW: frontend/src/components/StructuredDataView.tsx - Reusable component
UI Design:


Call Outcome: In-Transit Update
Driver Status: Driving
Current Location: I-10 near Indio, CA
ETA: Tomorrow, 8:00 AM
Delay Reason: Heavy Traffic
POD Reminder Acknowledged: Yes
Phase 3: Complete Scenario 2 - Dynamic Emergency Protocol
3.1 Implement Mid-Call Emergency Detection
Problem: Currently emergency detection only happens post-call via transcript analysis

Solution: Real-time keyword monitoring in WebSocket handler

Files to Modify:

backend/app/services/llm/realtime.py - Add emergency trigger detection
backend/app/services/llm/prompts.py - Add emergency protocol prompts
Emergency Triggers:


EMERGENCY_KEYWORDS = [
    "accident", "crash", "blowout", "breakdown",
    "medical", "emergency", "injured", "hurt",
    "pulling over", "can't drive", "need help"
]
Detection Logic:


# In WebSocket message handler:
if detect_emergency_in_transcript(latest_transcript):
    context.switch_to_emergency()
    return generate_emergency_response()
3.2 Build Emergency Escalation Flow
Goal: Agent gathers critical info then states it's connecting to human dispatcher

Conversation Flow:

Detect emergency trigger
Immediate acknowledgment: "I understand, let me help you"
Safety check: "Is everyone safe?"
Gather critical info:
Emergency type
Injuries
Location
Load security
Escalation statement: "I'm connecting you to a human dispatcher now"
End call with escalation status
Files to Modify:

backend/app/services/llm/conversation.py - Add emergency conversation generator
backend/app/models/call.py - Ensure ESCALATED status is used
3.3 Emergency Notification System
Goal: Alert human dispatchers when emergency is detected

Files to Create:

NEW: backend/app/services/notifications.py - Email/SMS alerts
Implementation:

Trigger when call status → ESCALATED
Send notification with:
Driver name, phone
Emergency type
Location
Safety status
Link to call details
Integration Point:

backend/app/api/webhooks.py - Add notification trigger in call_ended handler
3.4 Frontend Emergency UI
Files to Modify:

frontend/src/pages/CallDetailsPage.tsx - Add emergency banner
frontend/src/components/EmergencyAlert.tsx - Visual indicator
UI Design:


🚨 EMERGENCY ESCALATION
Emergency Type: Breakdown
Safety Status: Driver confirmed everyone is safe
Location: I-15 North, Mile Marker 123
Load Secure: Yes
Status: Connected to Human Dispatcher
Phase 4: Task B - Dynamic Response Handling
4.1 Uncooperative Driver Handling
Implementation:

Track one-word responses count
After 3 attempts, probe: "I need a bit more detail to help you..."
After 5+ attempts: "I'll let you go for now. Please call back when you have more time."
Set call_outcome: "Unresponsive Driver"
Files to Modify:

backend/app/services/llm/realtime.py - Add response quality tracking
4.2 Noisy Environment Handling
Implementation:

Detect low-confidence transcriptions (Retell provides confidence scores)
Ask clarification: "I didn't quite catch that, could you repeat?"
Limit to 3 repetitions per topic
If still unclear, escalate: "I'm having trouble hearing you. Let me connect you to dispatch."
Files to Modify:

backend/app/services/llm/realtime.py - Add transcription confidence handling
4.3 Conflicting Driver Handling
Scenario: Driver says "I'm in Phoenix" but GPS shows Barstow

Implementation:

Non-confrontational approach: "Thanks for the update. Our system shows you near Barstow - just wanted to confirm which is correct?"
Accept driver's answer without argument
Flag discrepancy in structured data
Files to Modify:

backend/app/services/llm/prompts.py - Add conflict resolution prompts
backend/app/services/llm/schemas.py - Add location_discrepancy field
Phase 5: Voice Configuration Best Practices (Task A)
5.1 Optimize Retell Voice Settings
Current State: Agent model has fields but may not use optimal values

Recommended Settings:


# For human-like experience:
interruption_sensitivity = 1.0  # Allow natural interruptions
enable_backchannel = True  # "uh-huh", "I see"
ambient_sound = "office"  # Sounds like real dispatch
speaking_rate = 1.0  # Natural pace
response_delay = 100  # ms, slight pause feels natural
Files to Modify:

backend/app/services/retell/agent.py - Update default values
Frontend agent config form - Add descriptions/recommendations
5.2 Test Voice Settings
Testing Plan:

Create test agents with different configurations
Compare:
With/without backchannel
Different interruption sensitivities
Various speaking rates
Document optimal settings in README
Phase 6: Testing & Polish
6.1 End-to-End Testing
Test Cases:

Check-In - Driving

Trigger call with driver info
Simulate "I'm driving on I-10 near Indio"
Verify agent asks for ETA, delays, POD
Confirm structured data extraction
Check-In - Arrived

Simulate "I just arrived at the warehouse"
Verify agent asks about unloading, door number
Confirm data extraction
Emergency - Mid-Call Switch

Start normal check-in
Interrupt with "I just had a blowout!"
Verify protocol switch
Confirm emergency data extraction
Verify escalation status
Edge Case - Uncooperative

Give one-word answers
Verify probing questions
Confirm graceful call end
Edge Case - Noisy

Simulate garbled speech
Verify clarification requests
Confirm escalation after retries
Web Call Testing

Test with Retell Web SDK in browser
Verify WebSocket connection
Confirm real-time responses
Files to Create:

backend/tests/test_websocket.py - WebSocket unit tests
backend/tests/test_scenarios.py - Scenario integration tests
6.2 Webhook Security
Implementation:

Validate Retell webhook signature
Use retell_webhook_secret_key from config
Files to Modify:

backend/app/api/webhooks.py - Add signature verification
6.3 Error Handling & Logging
Enhancements:

Graceful LLM failures (use fallback responses)
Database failure handling (retry logic)
WebSocket disconnection recovery
Comprehensive logging for debugging
Files to Modify:

All service files - Add try/catch with logging
backend/app/services/llm/realtime.py - Fallback responses
Critical Files by Component
Backend - Core Voice Engine
backend/app/api/websocket.py - NEW WebSocket endpoint
backend/app/services/llm/realtime.py - NEW Real-time LLM handler
backend/app/services/llm/context.py - NEW Conversation state
backend/app/services/llm/prompts.py - MODIFY Add scenario templates
backend/app/services/llm/extractor.py - MODIFY Incremental extraction
backend/app/services/retell/agent.py - MODIFY Optimal voice settings
Backend - Webhooks & Events
backend/app/api/webhooks.py - MODIFY Add signature verification, notifications
backend/app/services/notifications.py - NEW Emergency alerts
Frontend - Data Display
frontend/src/pages/CallDetailsPage.tsx - MODIFY Show structured data
frontend/src/components/StructuredDataView.tsx - NEW Data display component
frontend/src/components/EmergencyAlert.tsx - NEW Emergency banner
Configuration & Setup
backend/app/main.py - MODIFY Mount WebSocket routes
backend/.env - Ensure all Retell credentials present
Verification Steps
After Implementation:
Test WebSocket Connectivity

# Start backend
cd backend && source .venv/bin/activate && uvicorn app.main:app --reload

# Test WebSocket endpoint exists
curl http://localhost:8000/ws/llm
Test Check-In Scenario
Create check-in agent via UI
Trigger test call (use web call if outside USA)
Monitor backend logs for WebSocket messages
Verify conversation flow
Check structured data extraction in UI
Test Emergency Scenario
Create emergency agent via UI
Trigger test call
Interrupt with emergency phrase
Verify protocol switch
Confirm escalation status
Check emergency notification sent
Test Edge Cases
Trigger call with uncooperative responses
Verify graceful handling
Test noisy environment simulation
Verify clarification flow
Review Call History
Verify all calls are logged
Check structured data is displayed
Confirm transcripts are saved
Verify dashboard stats are accurate
Timeline Estimate
Phase 1 (WebSocket + Prompts): 8-10 hours
Phase 2 (Check-In Scenario): 4-6 hours
Phase 3 (Emergency Scenario): 4-6 hours
Phase 4 (Edge Cases): 3-4 hours
Phase 5 (Voice Optimization): 2-3 hours
Phase 6 (Testing & Polish): 4-5 hours
Total: ~25-34 hours of focused development

Success Criteria
✅ Agent can have natural, multi-turn conversation during calls
✅ Check-in scenario dynamically pivots based on driver status
✅ Emergency protocol immediately activates on trigger phrases
✅ All structured data fields are extracted correctly
✅ Frontend displays structured data in clean key-value format
✅ Edge cases are handled gracefully
✅ Web calls work for testing (important for non-USA developers)
✅ Code follows existing patterns and quality standards
✅ README documents all features and setup instructions