from functools import lru_cache

import chromadb

from jarvis.core.config import settings


@lru_cache(maxsize=1)
def get_chroma_client() -> chromadb.PersistentClient:
    # Uses an embedded persistent client — no separate service required.
    # Data is stored at settings.chroma_path (default: ./chroma_data).
    return chromadb.PersistentClient(path=settings.chroma_path)
