from __future__ import annotations

from pydantic import BaseModel, field_validator


class EvidenceRef(BaseModel):
    claim_text: str
    source_ids: list[str]
    chunk_ids: list[str] | None = None
    report_id: str

    @field_validator("source_ids")
    @classmethod
    def source_ids_not_empty(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("source_ids must contain at least one entry")
        return v
