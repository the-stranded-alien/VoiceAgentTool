# Retell AI Webhook Setup Guide

## Overview

This guide explains how to configure and test the Retell AI webhook integration.

## Webhook Configuration

### Port Configuration

**IMPORTANT:** The webhook and server must use the same port!

- **Server Port:** `8000` (configured in `app/config.py`)
- **Webhook URL:** `http://localhost:8000/api/v1/webhook/retell`

### Configuration Files

#### 1. `app/config.py`
```python
# Server configuration
port: int = 8000  # Uvicorn server port

# Webhook URL (must match the server port!)
server_url: str = "http://localhost:8000"
```

#### 2. `.env` file
```env
# Retell API Configuration
RETELL_API_KEY=your_api_key_here
RETELL_WEBHOOK_SECRET_KEY=your_webhook_secret_here

# Server URL for webhooks (update for production)
SERVER_URL=http://localhost:8000
```

## Webhook Endpoints

### 1. Test Endpoint (GET)
**URL:** `http://localhost:8000/api/v1/webhook/retell/test`

**Purpose:** Verify webhook is accessible

**Example:**
```bash
curl http://localhost:8000/api/v1/webhook/retell/test
```

**Response:**
```json
{
  "status": "ok",
  "message": "Retell webhook endpoint is accessible",
  "webhook_url": "POST http://localhost:8000/api/v1/webhook/retell"
}
```

### 2. Webhook Endpoint (POST)
**URL:** `http://localhost:8000/api/v1/webhook/retell`

**Purpose:** Receive events from Retell AI

**Supported Events:**
- `call_started` - When a call begins
- `call_ended` - When a call completes
- `call_analyzed` - When post-call analysis is ready

## Testing Webhooks

### Local Testing

1. **Start the server:**
```bash
cd backend
source .venv/bin/activate
python -m uvicorn app.main:app --reload --port 8000
```

2. **Run the webhook test script:**
```bash
python tests/test_webhook.py
```

3. **Manual test with curl:**
```bash
# Test with empty body
curl -X POST http://localhost:8000/api/v1/webhook/retell

# Test with call_started event
curl -X POST http://localhost:8000/api/v1/webhook/retell \
  -H "Content-Type: application/json" \
  -d '{
    "event": "call_started",
    "call": {
      "call_id": "test-123",
      "agent_id": "agent-456",
      "call_status": "in-progress"
    }
  }'
```

### Testing with Retell Dashboard

For local development, Retell cannot directly access `localhost`. Use one of these solutions:

#### Option 1: ngrok (Recommended)
```bash
# Install ngrok: https://ngrok.com/download
ngrok http 8000
```

This will give you a public URL like: `https://abc123.ngrok.io`

**Configure in Retell Dashboard:**
- Webhook URL: `https://abc123.ngrok.io/api/v1/webhook/retell`

#### Option 2: Other Tunneling Services
- [localtunnel](https://localtunnel.github.io/www/)
- [Cloudflare Tunnel](https://www.cloudflare.com/products/tunnel/)
- [serveo](https://serveo.net/)

## Production Deployment

### 1. Update Configuration

Update `.env` or `app/config.py`:
```env
SERVER_URL=https://your-production-domain.com
```

### 2. Configure Retell Dashboard

Set webhook URL to:
```
https://your-production-domain.com/api/v1/webhook/retell
```

### 3. Security Considerations

- ✅ Use HTTPS in production (never HTTP)
- ✅ Implement webhook signature verification (use `retell_webhook_secret_key`)
- ✅ Add rate limiting
- ✅ Monitor webhook failures
- ✅ Set up alerts for webhook errors

## Webhook Event Handling

### Event: `call_started`
Triggered when a call begins.

**Payload Example:**
```json
{
  "event": "call_started",
  "call": {
    "call_id": "call_abc123",
    "agent_id": "agent_456",
    "from_number": "+1234567890",
    "to_number": "+0987654321",
    "call_type": "web_call",
    "call_status": "ongoing"
  }
}
```

### Event: `call_ended`
Triggered when a call ends.

**Payload Example:**
```json
{
  "event": "call_ended",
  "call": {
    "call_id": "call_abc123",
    "agent_id": "agent_456",
    "call_status": "ended",
    "end_timestamp": 1234567890,
    "transcript": "Full call transcript...",
    "call_analysis": {...}
  }
}
```

### Event: `call_analyzed`
Triggered when post-call analysis completes.

**Payload Example:**
```json
{
  "event": "call_analyzed",
  "call": {
    "call_id": "call_abc123",
    "call_analysis": {
      "call_successful": true,
      "user_sentiment": "Positive",
      "call_summary": "Summary of the call..."
    }
  }
}
```

## Troubleshooting

### Issue: "Expecting value: line 1 column 1 (char 0)"
**Cause:** Empty request body

**Solution:**
- Check that Retell is sending proper JSON
- Webhook endpoint now handles empty bodies gracefully
- Use test endpoint to verify webhook is accessible

### Issue: Webhook not receiving events
**Checklist:**
- ✅ Server is running on correct port (8000)
- ✅ Webhook URL in Retell dashboard is correct
- ✅ Using public URL (ngrok) for local testing
- ✅ Check server logs for incoming requests

### Issue: Port mismatch
**Cause:** `server_url` config doesn't match actual server port

**Solution:**
```python
# app/config.py - These must match!
port: int = 8000
server_url: str = "http://localhost:8000"  # Port must be 8000
```

## Monitoring

### Check Webhook Status
```bash
# View recent webhook requests in logs
tail -f logs/app.log | grep webhook

# Test endpoint health
curl http://localhost:8000/api/v1/webhook/retell/test
```

### Debug Mode
Set `debug: True` in config to see detailed logs including:
- Request headers
- Raw request body
- JSON parsing details
- Event routing

## API Documentation

Once the server is running, view the auto-generated API docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

The webhook endpoints will be listed under the "webhooks" tag.
