# Layer Contracts: Knowledge Model Foundation

**Feature**: 001-knowledge-model
**Date**: 2026-05-31

This document defines what each architectural layer MUST produce and consume in terms of the
knowledge model types. These are internal contracts between layers — not external HTTP APIs.
All types are defined in `src/jarvis/models/`.

---

## Contract: Ingestion Layer → Knowledge Store

**Producer**: `ingestion/` layer
**Consumer**: `memory/` (knowledge store) and `retrieval/` layer

### Ingestion MUST produce

On receiving a raw source record:

1. One `SourceItem` with:
   - All required fields populated (source_type, source_name, canonical_id, source_url,
     body_text, retrieval_text, created_at, updated_at, privacy_label)
   - `processing_status = PENDING`
   - `deleted_at = None`
   - Optional fields (`summary`, `project`) populated when available from the source

2. On chunking completion, one or more `SourceChunk` records with:
   - `parent_id` = `SourceItem.canonical_id`
   - `chunk_index` starting at 0, sequential with no gaps
   - `char_count` = `len(chunk_text)` exactly
   - `char_count` ≤ 2000
   - `embedding = None` (chunking stage; embedding not yet computed)
   - Parent `SourceItem.processing_status` updated to `CHUNKED`

3. On embedding completion:
   - Each `SourceChunk.embedding` populated with the float vector
   - Parent `SourceItem.processing_status` updated to `EMBEDDED`

4. On any failure at any stage:
   - Parent `SourceItem.processing_status` set to `FAILED`
   - Partial state retained (do not delete the SourceItem on failure)

### Upsert contract

When `canonical_id` already exists:
- Update all fields on the existing `SourceItem` EXCEPT `canonical_id` and `created_at`
- Set `updated_at` to current time
- Set `processing_status` back to `PENDING`
- Delete all existing `SourceChunks` for this `canonical_id` and re-create from scratch

---

## Contract: Retrieval Layer → Agents and Reports

**Producer**: `retrieval/` layer
**Consumer**: `agents/` layer (tool calls) and `reports/` layer

### Retrieval MUST produce

For each query result, one `RetrievalResult` with:
- `chunk_id`, `parent_id`, `source_url`, `source_type` all populated (no None values)
- `retrieval_score` in [0.0, 1.0]
- `retrieval_mode` set to the mode used for this result
- `chunk_text` is the actual matched text (not a truncated preview)

### Retrieval MUST filter by default

- Exclude any `SourceItem` where `deleted_at IS NOT None` (soft-deleted)
- Exclude any `SourceChunk` whose parent has `deleted_at IS NOT None`
- Callers MAY pass `include_deleted=True` to override

### Retrieval MAY filter by caller request

- `privacy_label` filter (optional caller-supplied; not enforced automatically)
- `source_type` filter
- `project` filter
- Date range filter (for TEMPORAL mode)

---

## Contract: Reports Layer → Evidence References

**Producer**: `reports/` layer
**Consumer**: End user (report output)

### Reports MUST produce

For each substantive claim in a report that draws on retrieved data, one `EvidenceRef` with:
- `claim_text` = the exact statement being cited
- `source_ids` = list with at least one `SourceItem.canonical_id`
- `report_id` = an identifier for the report being generated
- `chunk_ids` = populated when the claim comes from a specific SEMANTIC or HYBRID result

Reports MUST NOT make claims about private data without an associated EvidenceRef.

---

## Module Import Map

```
src/jarvis/models/
├── __init__.py              # re-exports all public types
├── source_item.py           # SourceItem, SourceType, PrivacyLabel, ProcessingStatus
├── source_chunk.py          # SourceChunk
├── retrieval.py             # RetrievalResult, RetrievalMode
└── evidence.py              # EvidenceRef
```

**Import pattern** (all layers use the same path):
```python
from jarvis.models import SourceItem, SourceChunk, RetrievalResult, EvidenceRef
from jarvis.models import SourceType, PrivacyLabel, ProcessingStatus, RetrievalMode
```

No layer imports from another layer's module. All shared types come exclusively from
`jarvis.models`.
