from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, field_validator

from jarvis.models.source_item import SourceType


class RetrievalMode(StrEnum):
    SEMANTIC = "SEMANTIC"
    EXACT = "EXACT"
    TEMPORAL = "TEMPORAL"
    HYBRID = "HYBRID"


class RetrievalResult(BaseModel):
    chunk_id: str
    parent_id: str
    source_url: str
    source_type: SourceType
    chunk_text: str
    retrieval_score: float = Field(ge=0.0, le=1.0)
    retrieval_mode: RetrievalMode

    @field_validator("retrieval_score")
    @classmethod
    def score_in_range(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError(f"retrieval_score must be in [0.0, 1.0], got {v}")
        return v
