from fastapi import APIRouter, Request, HTTPException
from typing import Dict, Any
import logging
from app.services.retell.webhook import get_webhook_handler

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/retell")
async def retell_webhook_endpoint(request: Request):
    """
    Main webhook endpoint for Retell AI events
    
    Retell SDK sends events here:
    - call_started
    - call_ended  
    - call_analyzed
    """
    try:
        # Parse incoming webhook payload
        payload: Dict[str, Any] = await request.json()
        event_type = payload.get("event")
        
        logger.info(f"Received Retell webhook: {event_type}")
        
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