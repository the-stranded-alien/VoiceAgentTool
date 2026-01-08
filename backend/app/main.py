from typing import Union

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api import api_router
from app.api.websocket import router as ws_router

settings = get_settings()

app = FastAPI(
    title="AI Voice Agent API",
    description="Backend API for AI Voice Agent Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, switch to frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount REST API routes
app.include_router(api_router, prefix="/api/v1")

# Mount WebSocket routes for Retell AI Custom LLM
app.include_router(ws_router, prefix="/ws", tags=["websocket"])

@app.get("/")
async def read_root():
    return {
        "message": "AI Voice Agent API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )