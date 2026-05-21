import logging

from langchain_core.tools import tool

from jarvis.memory.chroma import get_chroma_client

logger = logging.getLogger(__name__)

_COLLECTION = "notes"
_N_RESULTS = 5


@tool
def search_notes(query: str) -> str:
    """Search my personal notes for information relevant to the query.

    Args:
        query: A natural language question or topic to search for in notes.
    """
    try:
        client = get_chroma_client()
        collection = client.get_or_create_collection(_COLLECTION)
        if collection.count() == 0:
            return "No notes have been ingested yet. Run POST /ingest/notes first."
        results = collection.query(query_texts=[query], n_results=_N_RESULTS)
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        if not docs:
            return "No relevant notes found."
        passages = []
        for doc, meta in zip(docs, metas):
            title = meta.get("title", "unknown")
            section = meta.get("section", "")
            source = f"{section} / {title}" if section else title
            passages.append(f"[{source}]\n{doc}")
        return "\n\n---\n\n".join(passages)
    except Exception as e:
        logger.exception("search_notes failed")
        return f"Notes search error: {e}"
