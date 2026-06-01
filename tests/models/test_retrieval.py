import pytest
from pydantic import ValidationError

from jarvis.models import RetrievalMode, RetrievalResult, SourceType


def _make_result(**kwargs) -> dict:
    return {
        "chunk_id": "github:Jarvis#42::chunk::0",
        "parent_id": "github:Jarvis#42",
        "source_url": "https://github.com/jeffjames/Jarvis/issues/42",
        "source_type": SourceType.GITHUB,
        "chunk_text": "Add knowledge model We need a canonical SourceItem.",
        "retrieval_score": 0.92,
        "retrieval_mode": RetrievalMode.SEMANTIC,
        **kwargs,
    }


# T021 — required fields; retrieval_score valid in [0.0, 1.0]
def test_retrieval_result_valid():
    result = RetrievalResult(**_make_result())
    assert result.retrieval_score == 0.92
    assert result.retrieval_mode == RetrievalMode.SEMANTIC
    assert result.source_type == SourceType.GITHUB


def test_retrieval_result_score_boundary_zero():
    result = RetrievalResult(**_make_result(retrieval_score=0.0))
    assert result.retrieval_score == 0.0


def test_retrieval_result_score_boundary_one():
    result = RetrievalResult(**_make_result(retrieval_score=1.0))
    assert result.retrieval_score == 1.0


def test_retrieval_result_all_modes():
    for mode in RetrievalMode:
        result = RetrievalResult(**_make_result(retrieval_mode=mode))
        assert result.retrieval_mode == mode


# T022 — ValidationError when retrieval_score outside [0.0, 1.0]
def test_retrieval_result_score_too_high():
    with pytest.raises(ValidationError):
        RetrievalResult(**_make_result(retrieval_score=1.1))


def test_retrieval_result_score_negative():
    with pytest.raises(ValidationError):
        RetrievalResult(**_make_result(retrieval_score=-0.1))
