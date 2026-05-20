from fastapi import APIRouter

from jarvis.core.config import settings

router = APIRouter()


@router.get("/")
async def root():
    return {"message": f"Hello from {settings.app_name}"}


@router.get("/health")
async def health():
    return {"status": "ok"}
