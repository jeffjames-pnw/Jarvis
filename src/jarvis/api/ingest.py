import logging

from fastapi import APIRouter, BackgroundTasks, Depends

from jarvis.core.auth import require_api_key
from jarvis.ingest.onenote import ingest_all_pages

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ingest", tags=["ingest"], dependencies=[Depends(require_api_key)])


def _run_ingest() -> None:
    try:
        result = ingest_all_pages()
        logger.info("ingest_notes completed", extra=result)
    except Exception:
        logger.exception("ingest_notes background task failed")


@router.post("/notes", status_code=202)
async def ingest_notes(background_tasks: BackgroundTasks) -> dict:
    """Trigger OneNote ingestion into ChromaDB. Returns immediately; runs in the background.

    Check Render logs for completion. Safe to re-run — upsert overwrites existing chunks.
    Requires MICROSOFT_CLIENT_ID and MICROSOFT_REFRESH_TOKEN to be set.
    """
    background_tasks.add_task(_run_ingest)
    return {"status": "accepted", "message": "Ingestion started — check logs for progress"}
