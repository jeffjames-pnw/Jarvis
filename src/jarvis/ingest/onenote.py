import logging
from typing import Any

import httpx
import msal
from bs4 import BeautifulSoup

from jarvis.core.config import settings
from jarvis.memory.chroma import get_chroma_client

logger = logging.getLogger(__name__)

_AUTHORITY = "https://login.microsoftonline.com/common"
_SCOPES = ["https://graph.microsoft.com/Notes.Read"]  # offline_access handled by MSAL internally
_GRAPH_BASE = "https://graph.microsoft.com/v1.0/me/onenote"
_COLLECTION = "notes"
_CHUNK_SIZE = 800  # characters per ChromaDB document


def _get_access_token() -> str:
    app = msal.PublicClientApplication(
        settings.microsoft_client_id,
        authority=_AUTHORITY,
    )
    result = app.acquire_token_by_refresh_token(
        settings.microsoft_refresh_token,
        scopes=_SCOPES,
    )
    if "access_token" not in result:
        raise RuntimeError(f"Token refresh failed: {result.get('error_description')}")
    return result["access_token"]


def _fetch_pages(token: str) -> list[dict[str, Any]]:
    headers = {"Authorization": f"Bearer {token}"}
    pages = []
    url = f"{_GRAPH_BASE}/pages?$select=id,title,parentSection&$top=100"
    while url:
        resp = httpx.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        pages.extend(data.get("value", []))
        url = data.get("@odata.nextLink")
    return pages


def _fetch_page_content(token: str, page_id: str) -> str:
    headers = {"Authorization": f"Bearer {token}"}
    resp = httpx.get(f"{_GRAPH_BASE}/pages/{page_id}/content", headers=headers, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    return soup.get_text(separator="\n", strip=True)


def _chunk(text: str, size: int = _CHUNK_SIZE) -> list[str]:
    # Split on paragraph breaks first, then hard-cut if still too long
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks, current = [], ""
    for para in paragraphs:
        if len(current) + len(para) > size and current:
            chunks.append(current.strip())
            current = para
        else:
            current = f"{current}\n\n{para}" if current else para
    if current:
        chunks.append(current.strip())
    return chunks


def ingest_all_pages() -> dict[str, int]:
    """Pull all OneNote pages, chunk them, and upsert into ChromaDB."""
    token = _get_access_token()
    pages = _fetch_pages(token)
    logger.info("fetched %d OneNote pages", len(pages))

    client = get_chroma_client()
    collection = client.get_or_create_collection(_COLLECTION)

    added = 0
    for page in pages:
        page_id = page["id"]
        title = page.get("title", "Untitled")
        try:
            content = _fetch_page_content(token, page_id)
        except Exception:
            logger.warning("failed to fetch page %s (%s)", page_id, title)
            continue

        chunks = _chunk(content)
        ids = [f"{page_id}_{i}" for i in range(len(chunks))]
        metas = [{"title": title, "page_id": page_id, "chunk": i} for i in range(len(chunks))]
        collection.upsert(documents=chunks, ids=ids, metadatas=metas)
        added += len(chunks)

    logger.info("upserted %d chunks into ChromaDB collection '%s'", added, _COLLECTION)
    return {"pages": len(pages), "chunks": added}
