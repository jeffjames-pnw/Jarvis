# Quickstart: Knowledge Model Foundation

**Feature**: 001-knowledge-model

This guide shows how to use the Jarvis knowledge model entities once implemented.

## Import Pattern

```python
from jarvis.models import SourceItem, SourceChunk, RetrievalResult, EvidenceRef
from jarvis.models import SourceType, PrivacyLabel, ProcessingStatus, RetrievalMode
```

## Create a SourceItem from a GitHub Issue

```python
from datetime import datetime, timezone
from jarvis.models import SourceItem, SourceType, PrivacyLabel, ProcessingStatus

item = SourceItem(
    source_type=SourceType.GITHUB,
    source_name="Jarvis",
    canonical_id="github:jeffjames/Jarvis#issue:42",
    source_url="https://github.com/jeffjames/Jarvis/issues/42",
    body_text="## Add knowledge model\n\nWe need a canonical SourceItem...",
    retrieval_text="Add knowledge model We need a canonical SourceItem...",
    created_at=datetime(2026, 5, 1, tzinfo=timezone.utc),
    updated_at=datetime(2026, 5, 31, tzinfo=timezone.utc),
    project="Jarvis",
)
# Defaults: privacy_label=PRIVATE, processing_status=PENDING, deleted_at=None
```

## Create SourceChunks from a SourceItem

```python
from jarvis.models import SourceChunk

chunks = [
    SourceChunk(
        chunk_id="github:jeffjames/Jarvis#issue:42::chunk::0",
        parent_id="github:jeffjames/Jarvis#issue:42",
        chunk_index=0,
        chunk_text="Add knowledge model We need a canonical SourceItem...",
        char_count=53,
    )
]
# embedding defaults to None until the embedding stage runs
```

## Soft-Delete a SourceItem

```python
from datetime import datetime, timezone

item.deleted_at = datetime.now(timezone.utc)
# This item will now be excluded from retrieval by default
```

## Wrap a Search Result as a RetrievalResult

```python
from jarvis.models import RetrievalResult, RetrievalMode

result = RetrievalResult(
    chunk_id="github:jeffjames/Jarvis#issue:42::chunk::0",
    parent_id="github:jeffjames/Jarvis#issue:42",
    source_url="https://github.com/jeffjames/Jarvis/issues/42",
    source_type=SourceType.GITHUB,
    chunk_text="Add knowledge model We need a canonical SourceItem...",
    retrieval_score=0.92,
    retrieval_mode=RetrievalMode.SEMANTIC,
)
```

## Create an EvidenceRef for a Report Claim

```python
from jarvis.models import EvidenceRef

ref = EvidenceRef(
    claim_text="The knowledge model feature was created on May 31, 2026.",
    source_ids=["github:jeffjames/Jarvis#issue:42"],
    chunk_ids=["github:jeffjames/Jarvis#issue:42::chunk::0"],
    report_id="weekly-report-2026-W22",
)
```

## Validation Errors

Invalid records raise `ValidationError` immediately:

```python
# Missing required field — raises ValidationError
SourceItem(source_type=SourceType.GITHUB)  # missing canonical_id, etc.

# Unknown source_type — raises ValidationError (UNKNOWN is accepted, others are not)
SourceItem(source_type="SLACK", ...)

# char_count exceeds maximum — raises ValidationError
SourceChunk(char_count=2500, chunk_text="x" * 2500, ...)

# Empty source_ids — raises ValidationError
EvidenceRef(claim_text="...", source_ids=[], report_id="r1")
```

## Running Tests

```bash
uv run pytest tests/models/ -v
```

All tests use fixture data and require no API keys or external services.
