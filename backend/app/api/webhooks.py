from fastapi import APIRouter, Request, HTTPException
from typing import Dict, Any
import logging
from app.services.retell.webhook import get_webhook_handler

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/retell/test")
async def test_webhook_endpoint():
    """
    Test endpoint to verify webhook is accessible

    Access at: http://localhost:8000/api/v1/webhook/retell/test
    """
    return {
        "status": "ok",
        "message": "Retell webhook endpoint is accessible",
        "webhook_url": "POST http://localhost:8000/api/v1/webhook/retell",
        "note": "Use this URL when configuring webhooks in Retell dashboard"
    }

@router.post("/retell")
async def retell_webhook_endpoint(request: Request):
    """
    Main webhook endpoint for Retell AI events

    Retell SDK sends events here:
    - call_started
    - call_ended
    - call_analyzed

    Full webhook URL: http://your-domain:8000/api/v1/webhook/retell
    """
    try:
        # Log request details for debugging
        logger.info(f"Webhook request received from {request.client.host}")
        logger.debug(f"Headers: {request.headers}")

        # Get request body
        body = await request.body()
        logger.debug(f"Raw body: {body}")

        # Handle empty body
        if not body:
            logger.warning("Received empty webhook body")
            return {
                "status": "ok",
                "message": "Webhook endpoint is active (received empty body)"
            }

        # Parse incoming webhook payload
        try:
            payload: Dict[str, Any] = await request.json()
        except Exception as json_error:
            logger.error(f"Failed to parse JSON: {json_error}")
            logger.error(f"Body was: {body.decode('utf-8') if body else 'empty'}")
            return {
                "status": "error",
                "message": "Invalid JSON payload"
            }

        event_type = payload.get("event")
        logger.info(f"Received Retell webhook event: {event_type}")
        logger.debug(f"Payload: {payload}")

        # Get webhook handler
        handler = get_webhook_handler()

        # Route to appropriate handler
        if event_type == "call_started":
            result = await handler.handle_call_started(payload)
        elif event_type == "call_ended":
            result = await handler.handle_call_ended(payload)
        elif event_type == "call_analyzed":
            result = await handler.handle_call_analyzed(payload)
        else:
            logger.warning(f"Unknown event type: {event_type}")
            result = {"status": "ignored", "message": f"Unknown event: {event_type}"}

        return result

    except Exception as e:
        logger.error(f"Webhook error: {str(e)}", exc_info=True)
        # Return 200 even on error to prevent Retell from retrying
        return {"status": "error", "message": str(e)}