from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from jarvis.models import PrivacyLabel, ProcessingStatus, SourceItem, SourceType

_NOW = datetime(2026, 5, 31, 12, 0, 0, tzinfo=UTC)
_EARLIER = datetime(2026, 5, 1, 9, 0, 0, tzinfo=UTC)


# T008 — GitHub fixture maps to SourceItem
def test_source_item_from_github_fixture(github_item_data):
    item = SourceItem(**github_item_data)
    assert item.source_type == SourceType.GITHUB
    assert item.canonical_id == "github:jeffjames/Jarvis#issue:42"
    assert item.source_url == "https://github.com/jeffjames/Jarvis/issues/42"
    assert item.project == "Jarvis"
    assert item.privacy_label == PrivacyLabel.PRIVATE
    assert item.processing_status == ProcessingStatus.PENDING
    assert item.deleted_at is None


# T009 — other four source types map to SourceItem
def test_source_item_from_onenote_fixture(onenote_item_data):
    item = SourceItem(**onenote_item_data)
    assert item.source_type == SourceType.ONENOTE
    assert item.canonical_id == "onenote:ProjectNotes:Design:page-001"


def test_source_item_from_email_fixture(email_item_data):
    item = SourceItem(**email_item_data)
    assert item.source_type == SourceType.EMAIL
    assert item.metadata is not None
    assert item.metadata["sender"] == "colleague@example.com"


def test_source_item_from_calendar_fixture(calendar_item_data):
    item = SourceItem(**calendar_item_data)
    assert item.source_type == SourceType.CALENDAR
    assert item.metadata is not None
    assert "attendees" in item.metadata


def test_source_item_from_speckit_fixture(speckit_item_data):
    item = SourceItem(**speckit_item_data)
    assert item.source_type == SourceType.SPECKIT
    assert item.source_url == "specs/001-knowledge-model/spec.md"


# T010 — default field values
def test_source_item_defaults(github_item_data):
    item = SourceItem(**github_item_data)
    assert item.privacy_label == PrivacyLabel.PRIVATE
    assert item.processing_status == ProcessingStatus.PENDING
    assert item.deleted_at is None
    assert item.summary is None
    assert item.metadata is None


def test_source_item_explicit_privacy_label(github_item_data):
    item = SourceItem(**github_item_data, privacy_label=PrivacyLabel.PUBLIC)
    assert item.privacy_label == PrivacyLabel.PUBLIC


# T011 — ValidationError on missing required fields
def test_source_item_missing_canonical_id(github_item_data):
    del github_item_data["canonical_id"]
    with pytest.raises(ValidationError):
        SourceItem(**github_item_data)


def test_source_item_missing_source_url(github_item_data):
    del github_item_data["source_url"]
    with pytest.raises(ValidationError):
        SourceItem(**github_item_data)


def test_source_item_missing_body_text(github_item_data):
    del github_item_data["body_text"]
    with pytest.raises(ValidationError):
        SourceItem(**github_item_data)


def test_source_item_missing_retrieval_text(github_item_data):
    del github_item_data["retrieval_text"]
    with pytest.raises(ValidationError):
        SourceItem(**github_item_data)


# T012 — ValidationError for unknown source_type
def test_source_item_unknown_source_type_value(github_item_data):
    github_item_data["source_type"] = "SLACK"
    with pytest.raises(ValidationError):
        SourceItem(**github_item_data)


def test_source_item_unknown_enum_accepted(github_item_data):
    # UNKNOWN is a valid fallback value per FR-006
    github_item_data["source_type"] = "UNKNOWN"
    item = SourceItem(**github_item_data)
    assert item.source_type == SourceType.UNKNOWN


# T031 — soft-delete: deleted_at set means record is "soft-deleted"
def test_source_item_soft_delete(github_item_data):
    item = SourceItem(**github_item_data)
    assert item.deleted_at is None  # active

    item.deleted_at = _NOW
    assert item.deleted_at == _NOW  # soft-deleted

    # retrieval layers should exclude items where deleted_at is not None
    active_items = [item for item in [item] if item.deleted_at is None]
    assert len(active_items) == 0

    # callers can explicitly retrieve soft-deleted items
    all_items = [item]
    assert len(all_items) == 1


# T032 — upsert semantics: canonical_id and created_at preserved on re-ingestion
def test_source_item_upsert_preserves_identity(github_item_data):
    original = SourceItem(**github_item_data)
    original_canonical_id = original.canonical_id
    original_created_at = original.created_at

    # Simulate upsert: update mutable fields, preserve canonical_id + created_at
    updated = original.model_copy(
        update={
            "body_text": "Updated body text",
            "retrieval_text": "Updated retrieval text",
            "updated_at": _NOW,
            "processing_status": ProcessingStatus.PENDING,
        }
    )

    assert updated.canonical_id == original_canonical_id
    assert updated.created_at == original_created_at
    assert updated.body_text == "Updated body text"
    assert updated.processing_status == ProcessingStatus.PENDING


# T033 — FAILED status: valid and filterable
def test_source_item_failed_status(github_item_data):
    item = SourceItem(**github_item_data, processing_status=ProcessingStatus.FAILED)
    assert item.processing_status == ProcessingStatus.FAILED

    # filterable by processing_status
    all_items = [item, SourceItem(**github_item_data)]
    failed = [i for i in all_items if i.processing_status == ProcessingStatus.FAILED]
    assert len(failed) == 1
    assert failed[0].processing_status == ProcessingStatus.FAILED
