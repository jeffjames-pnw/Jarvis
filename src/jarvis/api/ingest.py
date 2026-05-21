import logging

from fastapi import APIRouter, HTTPException

from jarvis.ingest.onenote import ingest_all_pages

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("/notes")
async def ingest_notes() -> dict:
    """Pull all OneNote pages and upsert them into ChromaDB.

    Requires MICROSOFT_CLIENT_ID and MICROSOFT_REFRESH_TOKEN to be set.
    Safe to re-run — uses upsert so existing chunks are overwritten, not duplicated.
    """
    try:
        result = ingest_all_pages()
        logger.info("ingest_notes completed", extra=result)
        return {"status": "ok", **result}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    except Exception as e:
        logger.exception("ingest_notes failed")
        raise HTTPException(status_code=500, detail="Ingestion failed") from e
