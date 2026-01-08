from fastapi import APIRouter
from .agents import router as agents_router
from .calls import router as calls_router
from .webhooks import router as webhook_router
from .dashboard import router as dashboard_router

api_router = APIRouter()

api_router.include_router(agents_router, prefix="/agents", tags=["agents"])
api_router.include_router(calls_router, prefix="/calls", tags=["calls"])
api_router.include_router(webhook_router, prefix="/webhook", tags=["webhooks"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])