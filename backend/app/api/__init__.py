from fastapi import APIRouter
from .agents import router as agents_router

api_router = APIRouter()

api_router.include_router(agents_router, prefix="/agents", tags=["agents"])