from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from jarvis.core.config import settings

_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def require_api_key(key: str = Security(_header)) -> None:
    if not settings.api_key:
        return  # API key not configured — open access (dev mode)
    if key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or missing API key"
        )
