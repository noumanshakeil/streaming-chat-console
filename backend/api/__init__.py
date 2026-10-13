from fastapi import APIRouter
from backend.api import health, chat, ui
api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(chat.router, prefix="/api", tags=["chat"])
api_router.include_router(ui.router, tags=["ui"])
