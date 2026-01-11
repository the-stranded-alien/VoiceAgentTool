# Voice Agent Tool

A comprehensive web application for configuring, testing, and managing AI voice agent calls for logistics dispatch operations. Built with React, TypeScript, FastAPI, and Supabase, using Retell AI for voice capabilities and Anthropic Claude for intelligent conversation handling.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Usage Guide](#usage-guide)
- [API Documentation](#api-documentation)
- [Architecture & Design Decisions](#architecture--design-decisions)
- [Testing](#testing)
- [Additional Notes](#additional-notes)

## Overview

The Voice Agent Tool is a full-stack application designed to streamline logistics dispatch operations through AI-powered voice agents. It enables dispatchers to:

- Configure and manage multiple voice agent profiles with custom behaviors
- Trigger automated check-in calls with drivers
- Handle emergency situations with dynamic protocol switching
- Extract structured data from conversations automatically
- Monitor call performance and review call history
- Manage call lifecycle events and analytics

The system integrates with Retell AI for voice infrastructure and uses Anthropic Claude for natural language understanding and response generation.

## Features

### 1. Agent Configuration Management

#### Create & Manage Agents
- **Create New Agents**: Build custom voice agent configurations with unique names, descriptions, and behaviors
- **Edit Existing Agents**: Update agent settings, prompts, and configurations at any time
- **Delete Agents**: Remove agents and automatically clean up associated Retell AI agents
- **Agent Status Management**: 
  - `active`: Agent is ready for use in calls
  - `draft`: Agent is being configured (hidden from main UI)
  - `inactive`: Agent is disabled but preserved

#### Immediate Retell Integration
- **Automatic Agent Creation**: When you create an agent in the UI, a corresponding Retell AI agent is immediately created
- **Retell Agent ID Storage**: The system automatically stores and manages Retell agent IDs for seamless integration
- **Synchronized Deletion**: Deleting an agent also removes the associated Retell agent

#### Voice Settings Configuration
- **Voice Selection**: Choose from Retell's voice library (defaults to "11labs-Adrian")
- **Response Delay**: Control how quickly the agent responds (default: 0.8 seconds)
- **Interruption Sensitivity**: Set how easily drivers can interrupt the agent (0-1 scale, default: 0.7)
- **Backchannel**: Enable natural conversation fillers like "uh-huh" and "I see"
  - Frequency control: low, medium, high
- **Filler Words**: Enable human-like speech patterns
- **Ambient Sound**: Optional background noise simulation
- **Speaking Rate**: Control speech speed (normal, slow, fast)

#### Advanced Settings
- **Max Call Duration**: Set maximum call length in minutes (default: 10)
- **Retry Attempts**: Configure retry logic for failed calls (default: 3)
- **Auto-Escalate Emergency**: Automatically escalate emergency calls to human dispatchers
- **Record Calls**: Enable/disable call recording

#### Scenario Types
- **Check-In**: Standard driver status updates and location tracking
- **Emergency**: Critical situation handling with immediate protocol switching
- **Delivery**: Delivery confirmation and POD (Proof of Delivery) tracking
- **Custom**: User-defined scenarios with custom prompts and extraction schemas

### 2. Call Management

#### Call Creation & Initiation
- **Create Call Records**: Pre-create call records with driver information before initiating
- **Phone Calls**: Initiate real phone calls to driver numbers (E.164 format required)
- **Web Calls**: Browser-based testing without requiring phone numbers
- **Dynamic Variables**: Pass driver name and load number to the agent for personalized conversations
- **Call Status Tracking**: Monitor calls through states: `initiated`, `in_progress`, `completed`, `failed`, `escalated`

#### Call History & Details
- **View All Calls**: Browse complete call history with filtering options
- **Call Details Page**: Comprehensive view of individual calls including:
  - Call outcome and status badges
  - Extracted structured data (scenario-specific)
  - Full conversation transcript
  - Call recording playback (when available)
  - Technical details (Retell call IDs, timestamps, duration)
  - Call events timeline
- **Recent Calls Dashboard**: Quick access to the 10 most recent calls
- **Filtering**: Filter calls by status, agent configuration, or date range

#### Call Events Tracking
- **Event Types**:
  - `call_started`: When a call begins
  - `call_ended`: When a call terminates
  - `call_completed`: When a call finishes successfully
  - `emergency_detected`: When an emergency is identified mid-conversation
- **Event Data**: Each event stores relevant metadata and timestamps
- **Event History**: View complete event timeline for any call

#### Call Data Management
- **Delete Calls**: Remove individual call records
- **Delete Call Events**: Remove specific events or all events for a call
- **Bulk Operations**: Clear all calls and events (useful for testing)

#### Transcript Processing
- **Post-Call Processing**: Manually process transcripts to extract structured data
- **Re-extraction**: Re-run data extraction on existing transcripts with updated schemas

### 3. Real-Time Conversation Handling

#### WebSocket-Based Communication
- **Low-Latency Responses**: Real-time LLM responses via WebSocket connection to Retell
- **Bidirectional Communication**: Agent receives user speech and generates responses instantly
- **Connection Management**: Automatic reconnection and error handling

#### Dynamic Scenario Switching
- **Emergency Detection**: Automatically detects emergency keywords mid-conversation
- **Protocol Switching**: Immediately abandons normal flow when emergency is detected
- **Context Preservation**: Maintains conversation context during scenario transitions

#### Intelligent Response Generation
- **Context-Aware Responses**: Agent uses full conversation history for coherent responses
- **Personalization**: Uses driver name and load number throughout conversation
- **Adaptive Questioning**: Adjusts questions based on driver status and responses
- **Natural Language**: Generates human-like responses with appropriate tone

#### Opening Messages
- **Proactive Greeting**: Agent speaks first with personalized opening message
- **Dynamic Content**: Opening message adapts based on available driver/load information
- **Missing Data Handling**: Gracefully handles cases where driver name or load number is unknown

### 4. Data Extraction & Structured Output

#### Scenario-Specific Extraction

**Check-In Scenario** extracts:
- `call_outcome`: "In-Transit Update" or "Arrival Confirmation"
- `driver_status`: "Driving", "Delayed", "Arrived", or "Unloading"
- `current_location`: Driver's current location (e.g., "I-10 near Indio, CA")
- `eta`: Estimated time of arrival
- `delay_reason`: "Heavy Traffic", "Weather", "Mechanical", "None", or "Other"
- `unloading_status`: Status if arrived (e.g., "In Door 42", "Waiting for Lumper")
- `pod_reminder_acknowledged`: Boolean indicating POD reminder acknowledgment

**Emergency Scenario** extracts:
- `call_outcome`: Always "Emergency Escalation"
- `emergency_type`: "Accident", "Breakdown", "Medical", or "Other"
- `safety_status`: Driver's safety confirmation
- `injury_status`: Injury information
- `emergency_location`: Exact emergency location
- `load_secure`: Boolean indicating load security
- `escalation_status`: Always "Connected to Human Dispatcher"

**Delivery Scenario** extracts:
- `call_outcome`: "Delivery Confirmed" or "Delivery Issues"
- `delivery_time`: When delivery was completed
- `pod_received`: Boolean indicating POD receipt
- `pod_number`: POD reference number
- `delivery_issues`: Any issues during delivery

#### Extraction Features
- **Incremental Extraction**: Extracts data throughout the conversation, not just at the end
- **Schema Validation**: Validates extracted data against predefined schemas
- **Error Handling**: Gracefully handles extraction failures and missing data
- **LLM-Powered**: Uses Claude for intelligent extraction from natural language

### 5. Edge Case Handling

#### Uncooperative Drivers
- **One-Word Response Detection**: Identifies when drivers give minimal responses
- **Probing Behavior**: After 3+ one-word responses, agent probes for more detail
- **Call Termination**: Ends call gracefully after 5+ one-word responses
- **Professional Closure**: Uses appropriate closing messages

#### Noisy Environments
- **Low Confidence Detection**: Identifies when transcription confidence is low
- **Clarification Requests**: Asks driver to repeat or clarify unclear responses
- **Escalation**: Escalates to human dispatcher after persistent connection issues
- **Poor Connection Handling**: Detects and handles poor audio quality

#### Location Conflicts
- **Route Verification**: Compares driver's stated location with expected route
- **Non-Confrontational Approach**: Politely verifies location without accusing driver
- **Keyword Matching**: Uses intelligent matching against route corridor data
- **Conflict Resolution**: Handles discrepancies professionally

#### Emergency Handling
- **Keyword Detection**: Detects emergency trigger phrases in real-time
- **Immediate Protocol Switch**: Abandons normal conversation immediately
- **Critical Information Gathering**: Prioritizes safety and location information
- **Automatic Escalation**: Connects to human dispatcher after gathering required info
- **Call Termination**: Ends call after collecting minimum required emergency data

#### Conversation Completion
- **Success Detection**: Automatically detects when conversation goals are met
- **Smart Ending**: Ends calls when all required data is gathered (no unnecessary "are you still there?" prompts)
- **Final Messages**: Provides appropriate closing statements based on call outcome
- **POD Reminder**: Ensures proof of delivery reminders are acknowledged before ending

### 6. Dashboard & Analytics

#### Statistics Overview
- **Total Calls**: Count of all calls made
- **Successful Calls**: Calls that completed successfully with required data
- **Emergency Calls**: Calls that triggered emergency protocol
- **In Progress Calls**: Currently active calls
- **Average Duration**: Average call length in seconds

#### Recent Calls Table
- **Quick Access**: View 10 most recent calls at a glance
- **Key Information**: Driver name, phone number, load number, status, duration
- **Status Badges**: Visual indicators for call status (completed, failed, escalated, in progress)
- **Quick Navigation**: Click any call to view full details

#### Performance Metrics
- **Agent Performance**: View performance metrics per agent configuration
- **Success Rates**: Track success rates by agent and scenario type
- **Trend Analysis**: Monitor call trends over time

### 7. Webhook Integration

#### Retell Webhook Events
- **Call Started**: Triggered when Retell initiates a call
- **Call Ended**: Triggered when a call terminates
- **Call Analyzed**: Triggered when Retell completes call analysis
- **Event Logging**: All webhook events are logged in the `call_events` table

#### Webhook Configuration
- **Endpoint**: `{SERVER_URL}/api/v1/webhook/retell`
- **Security**: Webhook secret key validation
- **Error Handling**: Graceful handling of webhook failures
- **Test Endpoint**: Available at `/api/v1/webhook/retell/test` for verification

### 8. Database & Data Management

#### Database Features
- **PostgreSQL via Supabase**: Robust relational database
- **UUID Primary Keys**: All entities use UUIDs for unique identification
- **Timestamps**: Automatic created_at and updated_at tracking
- **JSONB Storage**: Flexible storage for voice settings, conversation rules, and structured data
- **Database Views**: Optimized views for recent calls and performance metrics
- **Indexes**: Optimized indexes for fast queries

#### Data Models
- **Agent Configs**: Store agent configurations with all settings
- **Calls**: Store call records with transcripts and extracted data
- **Call Events**: Store detailed event timeline for each call
- **Relationships**: Proper foreign key relationships between entities

## Tech Stack

### Frontend
- **React 19**: Latest React with modern hooks and features
- **TypeScript**: Type-safe development
- **Vite**: Fast build system and development server
- **Tailwind CSS**: Utility-first CSS framework for styling
- **React Router**: Client-side routing
- **Axios**: HTTP client for API communication
- **Lucide React**: Modern icon library
- **Vitest**: Testing framework

### Backend
- **FastAPI**: Modern Python web framework with automatic API documentation
- **Python 3.10+**: Modern Python features
- **Pydantic**: Data validation and serialization
- **Supabase**: PostgreSQL database with real-time capabilities
- **Retell SDK**: Voice AI infrastructure
- **Anthropic Claude API**: Large language model for conversation and extraction
- **WebSockets**: Real-time bidirectional communication
- **Uvicorn**: ASGI server for FastAPI

### Infrastructure
- **PostgreSQL**: Relational database (via Supabase)
- **Retell AI**: Voice infrastructure and telephony
- **Anthropic**: LLM provider for Claude

## Project Structure

```
VoiceAgentTool/
├── frontend/
│   ├── src/
│   │   ├── components/          # Reusable UI components
│   │   │   ├── AgentConfig/     # Agent configuration components
│   │   │   ├── Dashboard/      # Dashboard components
│   │   │   ├── Layout/          # Layout components (Header, Sidebar)
│   │   │   └── common/          # Shared components (Button, Card, etc.)
│   │   ├── pages/               # Page containers
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── AgentConfigPage.tsx
│   │   │   ├── CallHistoryPage.tsx
│   │   │   ├── CallDetailsPage.tsx
│   │   │   └── TriggerCallPage.tsx
│   │   ├── services/            # API client services
│   │   ├── types/               # TypeScript interfaces
│   │   ├── hooks/               # Custom React hooks
│   │   ├── utils/               # Helper functions (formatters, etc.)
│   │   └── test/                # Test utilities and mocks
│   ├── public/                  # Static assets
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── vitest.config.ts
├── backend/
│   ├── app/
│   │   ├── api/                 # REST & WebSocket endpoints
│   │   │   ├── agents.py        # Agent CRUD endpoints
│   │   │   ├── calls.py         # Call management endpoints
│   │   │   ├── dashboard.py     # Dashboard statistics
│   │   │   ├── webhooks.py      # Retell webhook handler
│   │   │   └── websocket.py     # WebSocket handler for real-time LLM
│   │   ├── services/            # Business logic
│   │   │   ├── agent_service.py # Agent management service
│   │   │   ├── call_service.py  # Call management service
│   │   │   ├── llm/             # LLM-related services
│   │   │   │   ├── base.py      # Base LLM interface
│   │   │   │   ├── context.py   # Conversation context management
│   │   │   │   ├── conversation.py # Conversation handling
│   │   │   │   ├── extractor.py # Data extraction
│   │   │   │   ├── prompts.py   # Prompt templates
│   │   │   │   ├── realtime.py  # Real-time LLM handler
│   │   │   │   └── schemas.py   # Extraction schemas
│   │   │   └── retell/          # Retell integration
│   │   │       ├── agent.py     # Retell agent management
│   │   │       ├── call.py      # Retell call management
│   │   │       ├── client.py     # Retell SDK wrapper
│   │   │       └── webhook.py    # Webhook event handling
│   │   ├── models/              # Pydantic schemas
│   │   │   ├── agent.py         # Agent models
│   │   │   └── call.py          # Call models
│   │   ├── database.py          # Database connection
│   │   ├── config.py            # Configuration management
│   │   └── main.py              # FastAPI application entry
│   ├── db/                      # Database migrations
│   │   ├── 001_uuid_extension.sql
│   │   ├── 002_create_agents_configs_table.sql
│   │   ├── 003_create_calls_table.sql
│   │   ├── 004_create_call_events_table.sql
│   │   ├── 005_create_indexes.sql
│   │   ├── 006_create_update_function.sql
│   │   ├── 007_insert_sample_agents_config.sql
│   │   ├── 008_create_view_for_recent_calls.sql
│   │   ├── 009_create_agent_performace_view.sql
│   │   ├── 010_create_stats_function.sql
│   │   └── 011_retell_agent_id_alter.sql
│   ├── requirements.txt
│   └── test_all_scenarios.py
└── README.md
```

## Setup Instructions

### Prerequisites

- **Node.js 18+** and npm
- **Python 3.10+**
- **Supabase account** (free tier works)
- **Retell AI account** (with API key)
- **Anthropic API key** (for Claude)

### Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a `.env` file** in the backend directory with the following variables:
   ```env
   # Supabase Configuration
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_PUBLISHABLE_KEY=your_anon_key
   SUPABASE_SECRET_KEY=your_service_role_key

   # Database Connection
   DATABASE_URL=postgresql://postgres:password@db.xxx.supabase.co:5432/postgres
   DATABASE_NAME=postgres
   DATABASE_PASSWORD=your_db_password

   # Retell AI Configuration
   RETELL_API_KEY=your_retell_api_key
   RETELL_WEBHOOK_SECRET_KEY=your_webhook_secret

   # Anthropic Claude API
   ANTHROPIC_API_KEY=your_anthropic_api_key

   # Server URL (for webhooks and WebSocket)
   SERVER_URL=https://your-ngrok-or-public-url
   # For local development with ngrok: https://abc123.ngrok.io
   ```

5. **Run database migrations:**
   - Open Supabase SQL Editor
   - Execute each SQL file in `db/` folder in numerical order (001, 002, 003, etc.)
   - This creates all necessary tables, views, and functions

6. **Start the backend server:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   The API will be available at `http://localhost:8000`
   API documentation at `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Create a `.env` file** in the frontend directory:
   ```env
   VITE_API_BASE_URL=http://localhost:8000/api/v1
   ```

4. **Start the development server:**
   ```bash
   npm run dev
   ```

5. **Open the application:**
   - Navigate to `http://localhost:5173` in your browser

### Retell AI Configuration

1. **Configure Webhook URL:**
   - In Retell dashboard, go to Webhook settings
   - Set webhook endpoint to: `{SERVER_URL}/api/v1/webhook/retell`
   - Enable events: `call_started`, `call_ended`, `call_analyzed`

2. **For Phone Calls:**
   - Ensure you have a phone number configured in Retell
   - Phone numbers must be in E.164 format (e.g., +1234567890)

3. **For Web Calls (Testing):**
   - No phone number required
   - Use browser-based testing via Retell Web SDK
   - Perfect for development and testing

### Local Development with ngrok

For local development, use ngrok to expose your backend:

1. **Install ngrok:**
   ```bash
   # macOS
   brew install ngrok
   
   # Or download from https://ngrok.com
   ```

2. **Start ngrok:**
   ```bash
   ngrok http 8000
   ```

3. **Update `.env` file:**
   ```env
   SERVER_URL=https://your-ngrok-url.ngrok.io
   ```

4. **Update Retell webhook URL** to use the ngrok URL

## Usage Guide

### Creating an Agent Configuration

1. **Navigate to "Agent Config"** in the sidebar
2. **Click "Create New Agent"**
3. **Fill in the form:**
   - **Name**: Descriptive name for the agent (e.g., "Morning Check-In Agent")
   - **Description**: Optional description of the agent's purpose
   - **Scenario Type**: Choose from:
     - `check_in`: Standard driver check-in
     - `emergency`: Emergency protocol handler
     - `delivery`: Delivery confirmation
     - `custom`: Custom scenario
   - **System Prompt**: Custom instructions for the agent (or use defaults)
   - **Voice Settings**: Configure voice parameters
   - **Advanced Settings**: Set call duration limits, retry attempts, etc.
   - **Status**: Set to `active` to make it available for calls
4. **Click "Save"**
   - The system automatically creates a Retell agent
   - The Retell agent ID is stored in the database

### Triggering a Test Call

1. **Navigate to "Trigger Call"** in the sidebar
2. **Select an agent configuration** from the dropdown
3. **Enter driver details:**
   - **Driver Name**: Name of the driver (e.g., "John Smith")
   - **Phone Number**: E.164 format (e.g., +1234567890) OR
   - **Web Call**: Check this box for browser-based testing
   - **Load Number**: Optional load/tracking number (enables route conflict detection)
4. **Click "Start Call"**
   - For phone calls: Call is initiated immediately
   - For web calls: You'll receive an access token to use with Retell Web SDK

### Viewing Call Results

1. **Navigate to "Call History"** to see all calls
2. **Click on any call** to view details:
   - **Status Badge**: Visual indicator of call outcome
   - **Structured Data**: Extracted information based on scenario
   - **Transcript**: Full conversation transcript
   - **Recording**: Play call recording (if available)
   - **Events**: Timeline of call events
   - **Technical Details**: Retell IDs, timestamps, duration

### Dashboard Overview

1. **Navigate to "Dashboard"** for a quick overview
2. **View Statistics:**
   - Total calls made
   - Successful calls
   - Emergency calls
   - In-progress calls
3. **Recent Calls Table:**
   - Quick access to 10 most recent calls
   - Click any call to view full details

### Managing Agents

1. **Edit Agent:**
   - Click on an agent card in Agent Config page
   - Modify settings and save
   - Changes are immediately reflected

2. **Delete Agent:**
   - Click delete button on agent card
   - Confirms deletion
   - Removes both internal and Retell agents

3. **Filter Agents:**
   - Only active agents are shown by default
   - Draft agents are hidden from main view

### Managing Calls

1. **Delete Calls:**
   - Use API endpoint: `DELETE /api/v1/calls/{call_id}`
   - Removes call record and associated data

2. **Delete Call Events:**
   - Use API endpoint: `DELETE /api/v1/calls/events/{event_id}`
   - Or delete all events for a call: `DELETE /api/v1/calls/{call_id}/events`

3. **Clear All Data:**
   - Use API endpoint: `DELETE /api/v1/calls/recent-summary/all`
   - Clears all calls and events (useful for testing)

## API Documentation

### Agent Endpoints

- `POST /api/v1/agents/` - Create a new agent
- `GET /api/v1/agents/` - List all agents (with optional filters)
- `GET /api/v1/agents/{agent_id}` - Get specific agent
- `PUT /api/v1/agents/{agent_id}` - Update agent
- `DELETE /api/v1/agents/{agent_id}` - Delete agent
- `GET /api/v1/agents/performance/metrics` - Get agent performance metrics

### Call Endpoints

- `POST /api/v1/calls/` - Create a new call record
- `GET /api/v1/calls/` - List calls (with optional filters)
- `GET /api/v1/calls/{call_id}` - Get specific call
- `PUT /api/v1/calls/{call_id}` - Update call
- `POST /api/v1/calls/{call_id}/initiate` - Initiate call via Retell
- `GET /api/v1/calls/{call_id}/events` - Get call events
- `POST /api/v1/calls/{call_id}/events` - Create call event
- `POST /api/v1/calls/{call_id}/process-transcript` - Process transcript
- `DELETE /api/v1/calls/{call_id}` - Delete call
- `DELETE /api/v1/calls/events/{event_id}` - Delete call event
- `DELETE /api/v1/calls/{call_id}/events` - Delete all events for a call
- `DELETE /api/v1/calls/recent-summary/all` - Delete all calls
- `GET /api/v1/calls/stats/today` - Get today's statistics

### Dashboard Endpoints

- `GET /api/v1/dashboard/stats` - Get dashboard statistics

### Webhook Endpoints

- `POST /api/v1/webhook/retell` - Retell webhook handler
- `GET /api/v1/webhook/retell/test` - Test webhook endpoint

### WebSocket Endpoint

- `WS /ws/llm` - WebSocket endpoint for real-time LLM communication

**Full API Documentation**: Visit `http://localhost:8000/docs` when the backend is running for interactive Swagger documentation.

## Architecture & Design Decisions

### Separation of Concerns

- **Frontend**: Handles UI, user interactions, and API communication
- **Backend**: Manages business logic, Retell integration, and data persistence
- **Database**: Stores all persistent data with proper relationships

### Real-Time Communication

- **WebSocket for LLM**: Enables low-latency responses during active calls
- **Bidirectional**: Both Retell and backend can send messages
- **Connection Management**: Automatic reconnection and error recovery

### Scenario-Based Architecture

- **Modular Schemas**: Each scenario has its own extraction schema
- **Dynamic Switching**: System can switch scenarios mid-conversation
- **Extensible**: Easy to add new scenario types

### Voice Configuration Philosophy

- **Natural Conversation**: Backchannel and filler words for human-like interaction
- **Moderate Interruption**: Allows drivers to interject naturally
- **Short Responses**: Maintains natural dialogue flow
- **Configurable**: All voice parameters are adjustable per agent

### Edge Case Handling Strategy

- **Proactive Detection**: System detects issues early (one-word responses, low confidence)
- **Gradual Escalation**: Tries to resolve issues before escalating
- **Professional Closure**: Always ends calls professionally, even in failure cases
- **Context Preservation**: Maintains conversation context throughout edge cases

### Data Extraction Approach

- **Incremental**: Extracts data throughout conversation, not just at end
- **LLM-Powered**: Uses Claude for intelligent extraction from natural language
- **Schema Validation**: Validates extracted data against predefined schemas
- **Error Tolerance**: Handles missing or invalid data gracefully

### Call Lifecycle Management

- **Status Tracking**: Comprehensive status tracking from initiation to completion
- **Event Logging**: Detailed event timeline for debugging and analytics
- **Webhook Integration**: Synchronizes with Retell's call lifecycle events
- **Automatic Cleanup**: Proper cleanup of resources on call completion

## Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

### Manual Testing Scenarios

1. **Normal Check-In Call:**
   - Create agent with check_in scenario
   - Trigger call with driver name and load number
   - Verify agent speaks first
   - Verify structured data extraction

2. **Emergency Detection:**
   - Start normal check-in call
   - Driver mentions emergency keyword
   - Verify immediate protocol switch
   - Verify emergency data extraction
   - Verify call ends with escalation message

3. **Uncooperative Driver:**
   - Trigger call
   - Give one-word responses
   - Verify probing behavior after 3 responses
   - Verify call ends after 5+ responses

4. **Successful Completion:**
   - Trigger call with all required info
   - Complete conversation successfully
   - Verify call ends without unnecessary prompts
   - Verify all required data is extracted

## Additional Notes

### Phone Number Format

- **E.164 Format Required**: All phone numbers must be in E.164 format
- **Example**: `+1234567890` (includes country code, no spaces or dashes)
- **Web Calls**: No phone number needed for browser-based testing

### Route Conflict Detection

- The system includes mock route data for location conflict detection
- In production, this would integrate with GPS/route planning systems
- Location conflicts are detected using keyword matching against expected route corridors

### Emergency Keywords

Emergency detection is keyword-based and triggers on phrases like:
- "accident"
- "breakdown"
- "emergency"
- "help"
- "medical"
- And variations of these terms

### Call Status Definitions

- **initiated**: Call record created but not yet started
- **in_progress**: Call is currently active
- **completed**: Call finished successfully with required data
- **failed**: Call ended without completing objectives
- **escalated**: Call was escalated to human dispatcher (typically emergency)

### Retell Agent Creation

- Agents are created immediately when you save an agent configuration
- The Retell agent ID is automatically stored in the database
- If Retell agent creation fails, the internal agent is still created but marked appropriately
- Deleting an agent also deletes the associated Retell agent

### Database Views

The system uses optimized database views for:
- **Recent Calls**: Fast access to recent call summaries
- **Agent Performance**: Aggregated performance metrics per agent
- **Statistics**: Quick calculation of dashboard statistics

### WebSocket Message Flow

1. Retell connects to `/ws/llm` endpoint
2. Backend creates conversation context from call record
3. Backend sends opening message
4. Retell sends user utterances
5. Backend generates LLM response
6. Backend sends response to Retell
7. Process repeats until call ends
8. Backend saves final data and closes connection

### Error Handling

- **API Errors**: All endpoints return appropriate HTTP status codes
- **WebSocket Errors**: Errors are logged and connection is gracefully closed
- **Extraction Errors**: Missing data is handled gracefully, doesn't break call
- **Retell Errors**: Failures are logged and user is notified

### Performance Considerations

- **Database Indexes**: Optimized indexes for fast queries
- **Connection Pooling**: Efficient database connection management
- **Async Operations**: All I/O operations are asynchronous
- **Caching**: Consider implementing caching for frequently accessed data

### Security Considerations

- **API Keys**: Store all API keys in environment variables
- **Webhook Security**: Validate webhook signatures (when implemented)
- **CORS**: Configure CORS appropriately for production
- **Input Validation**: All inputs are validated using Pydantic models

### Future Enhancements

Potential areas for improvement:
- User authentication and authorization
- Multi-tenant support
- Advanced analytics and reporting
- Integration with external logistics systems
- Custom scenario builder UI
- Real-time call monitoring dashboard
- Automated testing suite
- Performance optimization for high-volume usage

---

**Built with ❤️ for efficient logistics dispatch operations**
