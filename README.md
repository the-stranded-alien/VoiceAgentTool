# Voice Agent Tool

A web application for configuring, testing, and reviewing AI voice agent calls for logistics dispatch operations. Built with React, TypeScript, FastAPI, and Supabase, using Retell AI for voice capabilities.

## Features

### Core Functionality

1. **Agent Configuration UI**
   - Create and manage voice agent configurations
   - Customize system prompts, voice settings, and conversation rules
   - Support for multiple scenarios: Check-in, Emergency, Delivery, Custom
   - Configure Retell AI voice parameters (backchannel, filler words, speaking rate)

2. **Call Triggering & Results**
   - Trigger phone calls or web calls (browser-based testing)
   - Enter driver name, phone number, and load number for context
   - View structured call results with scenario-specific data extraction
   - Full transcript display with recording playback

3. **Real-Time Conversation Handling**
   - WebSocket-based real-time LLM responses via Claude
   - Dynamic scenario switching (normal to emergency)
   - Edge case handling for uncooperative drivers and noisy environments

### Implemented Scenarios

**Scenario 1: Driver Check-In**
- Adaptive questioning based on driver status (Driving, Arrived, Delayed, Unloading)
- Extracts: location, ETA, delay reasons, unloading status, POD acknowledgment

**Scenario 2: Emergency Protocol**
- Keyword-triggered emergency detection mid-conversation
- Immediate protocol switch to gather critical information
- Extracts: emergency type, safety status, injury status, location, load security

### Dynamic Response Handling

- **Uncooperative Driver**: Probes for detail after 3+ one-word responses, ends call after 5+
- **Noisy Environment**: Requests clarification, escalates to human after persistent issues
- **Conflicting Location**: Non-confrontational verification when stated location differs from expected route

## Tech Stack

### Frontend
- React 19 + TypeScript
- Vite build system
- Tailwind CSS for styling
- React Router for navigation
- Axios for API communication

### Backend
- FastAPI (Python)
- Supabase (PostgreSQL) for data persistence
- Retell SDK for voice calls
- Anthropic Claude API for LLM responses
- WebSockets for real-time communication

## Project Structure

```
VoiceAgentTool/
├── frontend/
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Page containers
│   │   ├── services/       # API client
│   │   ├── types/          # TypeScript interfaces
│   │   └── utils/          # Helper functions
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── api/            # REST & WebSocket endpoints
│   │   ├── services/       # Business logic (LLM, Retell, etc.)
│   │   └── models/         # Pydantic schemas
│   ├── db/                 # Database migrations
│   └── requirements.txt
└── README.md
```

## Setup Instructions

### Prerequisites

- Node.js 18+ and npm
- Python 3.10+
- Supabase account
- Retell AI account
- Anthropic API key

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with the following variables:
   ```env
   # Supabase
   SUPABASE_URL=your_supabase_url
   SUPABASE_PUBLISHABLE_KEY=your_anon_key
   SUPABASE_SECRET_KEY=your_service_role_key

   # Database
   DATABASE_URL=your_postgres_connection_string
   DATABASE_NAME=postgres
   DATABASE_PASSWORD=your_db_password

   # Retell AI
   RETELL_API_KEY=your_retell_api_key
   RETELL_WEBHOOK_SECRET_KEY=your_webhook_secret

   # Anthropic
   ANTHROPIC_API_KEY=your_anthropic_api_key

   # Server (for webhook URL)
   SERVER_URL=https://your-ngrok-or-public-url
   ```

5. Run database migrations (execute SQL files in `db/` folder in Supabase)

6. Start the backend server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file:
   ```env
   VITE_API_BASE_URL=http://localhost:8000/api/v1
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

5. Open http://localhost:5173 in your browser

### Retell AI Configuration

1. In Retell dashboard, configure your webhook URL:
   - Set webhook endpoint to: `{SERVER_URL}/api/v1/webhook/retell`
   - Enable call_started, call_ended, and call_analyzed events

2. For phone calls, ensure you have a phone number configured in Retell

3. For web calls (testing), no additional phone number is needed

## Usage

### Creating an Agent Configuration

1. Navigate to "Agent Config" in the sidebar
2. Click "Create New Agent"
3. Fill in:
   - Name and description
   - Scenario type (check_in, emergency, delivery)
   - System prompt (or use defaults)
   - Voice settings (optional)
4. Save the configuration

### Triggering a Test Call

1. Navigate to "Trigger Call" in the sidebar
2. Select an agent configuration
3. Enter driver details:
   - Driver name
   - Phone number (E.164 format: +1234567890) OR use "Web Call" for browser testing
   - Load number (optional, but enables route conflict detection)
4. Click "Start Call"

### Viewing Results

1. Navigate to "Call History" to see all calls
2. Click on any call to view:
   - Call outcome badge with status
   - Extracted structured data (varies by scenario)
   - Full transcript
   - Recording (if available)
   - Technical details (Retell IDs, timestamps)

## Design Decisions

### Architecture

- **Separation of concerns**: Frontend handles UI, backend handles business logic and Retell integration
- **Real-time via WebSocket**: Enables low-latency LLM responses during active calls
- **Scenario-based extraction**: Different schemas for check-in vs emergency vs delivery

### Voice Configuration

- Backchannel enabled for natural conversation ("uh-huh", "I see")
- Moderate interruption sensitivity to allow driver to interject
- Filler words for human-like responses
- Short response length to maintain natural dialogue flow

### Edge Case Handling

- One-word response detection triggers probing behavior
- Low transcription confidence triggers clarification requests
- Location conflict detection uses keyword matching against expected route corridor
- Emergency keywords trigger immediate protocol switch

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

## Additional Notes

- For non-US users, use web calls instead of phone calls for testing
- The mock route data in `realtime.py` simulates GPS-based location conflict detection
- Emergency detection is keyword-based and triggers mid-conversation
