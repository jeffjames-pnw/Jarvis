import pytest
from pydantic import ValidationError

from jarvis.models import SourceChunk


def _make_chunk(**kwargs) -> dict:
    text = kwargs.pop("chunk_text", "Hello world, this is a chunk.")
    return {
        "chunk_id": "github:Jarvis#42::chunk::0",
        "parent_id": "github:Jarvis#42",
        "chunk_index": 0,
        "chunk_text": text,
        "char_count": len(text),
        **kwargs,
    }


# T015 — required fields accepted; char_count matches len(chunk_text)
def test_source_chunk_valid():
    data = _make_chunk()
    chunk = SourceChunk(**data)
    assert chunk.char_count == len(chunk.chunk_text)
    assert chunk.embedding is None


def test_source_chunk_multi_index():
    data = _make_chunk(chunk_index=2)
    chunk = SourceChunk(**data)
    assert chunk.chunk_index == 2


# T016 — ValidationError when char_count != len(chunk_text)
def test_source_chunk_char_count_mismatch():
    text = "Hello world"
    with pytest.raises(ValidationError, match="char_count"):
        SourceChunk(
            chunk_id="id",
            parent_id="parent",
            chunk_index=0,
            chunk_text=text,
            char_count=len(text) + 5,  # deliberate mismatch
        )


def test_source_chunk_char_count_too_low():
    text = "Hello world"
    with pytest.raises(ValidationError, match="char_count"):
        SourceChunk(
            chunk_id="id",
            parent_id="parent",
            chunk_index=0,
            chunk_text=text,
            char_count=1,  # deliberate mismatch
        )


# T017 — ValidationError when char_count > 2000
def test_source_chunk_exceeds_max_size():
    text = "x" * 2001
    with pytest.raises(ValidationError, match="2000"):
        SourceChunk(
            chunk_id="id",
            parent_id="parent",
            chunk_index=0,
            chunk_text=text,
            char_count=len(text),
        )


def test_source_chunk_at_max_size():
    text = "x" * 2000
    chunk = SourceChunk(
        chunk_id="id",
        parent_id="parent",
        chunk_index=0,
        chunk_text=text,
        char_count=len(text),
    )
    assert chunk.char_count == 2000


# T018 — embedding=None (default) and embedding=list[float] both valid
def test_source_chunk_embedding_none_by_default():
    chunk = SourceChunk(**_make_chunk())
    assert chunk.embedding is None


def test_source_chunk_embedding_list_float():
    embedding = [0.1, 0.2, 0.3, 0.4]
    chunk = SourceChunk(**_make_chunk(embedding=embedding))
    assert chunk.embedding == embedding
