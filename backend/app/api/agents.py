from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.database import get_supabase

from supabase import Client

router = APIRouter()

@router.get("/")
async def list_agents():
    return {"data": "agents"}