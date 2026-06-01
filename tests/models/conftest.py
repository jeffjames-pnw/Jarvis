from datetime import UTC, datetime

import pytest

_NOW = datetime(2026, 5, 31, 12, 0, 0, tzinfo=UTC)
_EARLIER = datetime(2026, 5, 1, 9, 0, 0, tzinfo=UTC)


@pytest.fixture
def github_item_data() -> dict:
    return {
        "source_type": "GITHUB",
        "source_name": "Jarvis",
        "canonical_id": "github:jeffjames/Jarvis#issue:42",
        "source_url": "https://github.com/jeffjames/Jarvis/issues/42",
        "body_text": "## Add knowledge model\n\nWe need a canonical SourceItem for all sources.",
        "retrieval_text": "Add knowledge model We need a canonical SourceItem for all sources.",
        "created_at": _EARLIER,
        "updated_at": _NOW,
        "project": "Jarvis",
    }


@pytest.fixture
def onenote_item_data() -> dict:
    return {
        "source_type": "ONENOTE",
        "source_name": "ProjectNotes",
        "canonical_id": "onenote:ProjectNotes:Design:page-001",
        "source_url": "https://onenote.com/pages/page-001",
        "body_text": "<html><body><p>Design decisions for Jarvis.</p></body></html>",
        "retrieval_text": "Design decisions for Jarvis knowledge model.",
        "created_at": _EARLIER,
        "updated_at": _NOW,
        "project": "ProjectNotes",
    }


@pytest.fixture
def email_item_data() -> dict:
    return {
        "source_type": "EMAIL",
        "source_name": "jeffjames.pnw@gmail.com",
        "canonical_id": "email:gmail:msg-abc123",
        "source_url": "https://mail.google.com/mail/u/0/#inbox/msg-abc123",
        "body_text": "Subject: Meeting follow-up\n\nHere are the action items from today's call.",
        "retrieval_text": "Meeting follow-up Here are the action items from today's call.",
        "created_at": _EARLIER,
        "updated_at": _NOW,
        "metadata": {"sender": "colleague@example.com", "recipients": ["jeffjames.pnw@gmail.com"]},
    }


@pytest.fixture
def calendar_item_data() -> dict:
    return {
        "source_type": "CALENDAR",
        "source_name": "jeffjames.pnw@gmail.com",
        "canonical_id": "calendar:google:evt-xyz789",
        "source_url": "https://calendar.google.com/event?eid=evt-xyz789",
        "body_text": "Sprint planning for Jarvis Q2 milestones.",
        "retrieval_text": "Sprint planning for Jarvis Q2 milestones.",
        "created_at": _EARLIER,
        "updated_at": _NOW,
        "metadata": {"attendees": ["jeffjames.pnw@gmail.com"], "location": "Remote"},
    }


@pytest.fixture
def speckit_item_data() -> dict:
    return {
        "source_type": "SPECKIT",
        "source_name": "001-knowledge-model",
        "canonical_id": "speckit:specs/001-knowledge-model/spec.md",
        "source_url": "specs/001-knowledge-model/spec.md",
        "body_text": "# Feature Specification: Knowledge Model Foundation\n\n...",
        "retrieval_text": "Feature Specification Knowledge Model Foundation ...",
        "created_at": _EARLIER,
        "updated_at": _NOW,
        "project": "001-knowledge-model",
    }
