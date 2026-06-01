from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class SourceType(StrEnum):
    GITHUB = "GITHUB"
    ONENOTE = "ONENOTE"
    EMAIL = "EMAIL"
    CALENDAR = "CALENDAR"
    SPECKIT = "SPECKIT"
    UNKNOWN = "UNKNOWN"


class PrivacyLabel(StrEnum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    PRIVATE = "PRIVATE"
    CONFIDENTIAL = "CONFIDENTIAL"


class ProcessingStatus(StrEnum):
    PENDING = "PENDING"
    CHUNKED = "CHUNKED"
    EMBEDDED = "EMBEDDED"
    FAILED = "FAILED"


class SourceItem(BaseModel):
    source_type: SourceType
    source_name: str
    canonical_id: str
    source_url: str
    body_text: str
    retrieval_text: str
    created_at: datetime
    updated_at: datetime
    privacy_label: PrivacyLabel = PrivacyLabel.PRIVATE
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    deleted_at: datetime | None = None
    project: str | None = None
    summary: str | None = None
    metadata: dict[str, Any] | None = Field(default=None)
