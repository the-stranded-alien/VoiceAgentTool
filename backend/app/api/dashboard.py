from fastapi import APIRouter, Depends
from app.database import get_supabase
from app.services.call_service import CallService
from app.models.call import TodayStatsResponse
from supabase import Client

router = APIRouter()

def get_call_service(supabase: Client = Depends(get_supabase)) -> CallService:
    return CallService(supabase)

@router.get("/stats", response_model=TodayStatsResponse)
async def get_dashboard_stats(
    service: CallService = Depends(get_call_service)
):
    """Get dashboard statistics (all-time stats)"""
    return await service.get_today_stats()
