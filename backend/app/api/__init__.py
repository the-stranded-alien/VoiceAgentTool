from fastapi import APIRouter
from .agents import router as agents_router
from .calls import router as calls_router

api_router = APIRouter()

api_router.include_router(agents_router, prefix="/agents", tags=["agents"])
api_router.include_router(calls_router, prefix="/calls", tags=["calls"])