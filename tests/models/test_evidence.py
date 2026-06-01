import pytest
from pydantic import ValidationError

from jarvis.models import EvidenceRef


def _make_ref(**kwargs) -> dict:
    return {
        "claim_text": "The knowledge model was created on May 31, 2026.",
        "source_ids": ["github:jeffjames/Jarvis#issue:42"],
        "report_id": "weekly-report-2026-W22",
        **kwargs,
    }


# T023 — required fields; non-empty source_ids
def test_evidence_ref_valid():
    ref = EvidenceRef(**_make_ref())
    assert ref.claim_text == "The knowledge model was created on May 31, 2026."
    assert len(ref.source_ids) == 1
    assert ref.chunk_ids is None
    assert ref.report_id == "weekly-report-2026-W22"


def test_evidence_ref_with_chunk_ids():
    ref = EvidenceRef(**_make_ref(chunk_ids=["github:Jarvis#42::chunk::0"]))
    assert ref.chunk_ids == ["github:Jarvis#42::chunk::0"]


def test_evidence_ref_multiple_source_ids():
    ref = EvidenceRef(**_make_ref(source_ids=["id:1", "id:2", "id:3"]))
    assert len(ref.source_ids) == 3


# T024 — ValidationError when source_ids is empty
def test_evidence_ref_empty_source_ids():
    with pytest.raises(ValidationError, match="source_ids"):
        EvidenceRef(**_make_ref(source_ids=[]))


def test_evidence_ref_missing_source_ids():
    data = _make_ref()
    del data["source_ids"]
    with pytest.raises(ValidationError):
        EvidenceRef(**data)
