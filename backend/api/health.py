from fastapi import APIRouter
from pydantic import BaseModel
from backend import __version__
from backend.config import settings

class HealthOut(BaseModel):
    status: str
    service: str
    version: str
    llm_mode: str

router = APIRouter()

@router.get("/health", response_model=HealthOut)
async def health():
    return HealthOut(
        status="ok",
        service=settings.app_name,
        version=__version__,
        llm_mode=settings.llm_mode,
    )
