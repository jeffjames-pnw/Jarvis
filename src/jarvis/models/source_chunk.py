from __future__ import annotations

from pydantic import BaseModel, model_validator


class SourceChunk(BaseModel):
    chunk_id: str
    parent_id: str
    chunk_index: int
    chunk_text: str
    char_count: int
    embedding: list[float] | None = None

    @model_validator(mode="after")
    def validate_char_count(self) -> SourceChunk:
        actual = len(self.chunk_text)
        if self.char_count != actual:
            raise ValueError(
                f"char_count ({self.char_count}) must equal len(chunk_text) ({actual})"
            )
        if self.char_count > 2000:
            raise ValueError(
                f"char_count ({self.char_count}) exceeds maximum of 2000 characters"
            )
        return self
