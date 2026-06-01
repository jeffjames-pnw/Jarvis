# Data Model: Knowledge Model Foundation

**Feature**: 001-knowledge-model
**Date**: 2026-05-31

## Enumerations

### SourceType

Values that identify which external system a SourceItem came from.

| Value | Description |
|---|---|
| `GITHUB` | GitHub repositories, issues, PRs, commits, discussions, milestones |
| `ONENOTE` | Microsoft OneNote notebook pages |
| `EMAIL` | Email messages (Gmail or Outlook — same type, same schema) |
| `CALENDAR` | Calendar events (Google Calendar or Outlook Calendar) |
| `SPECKIT` | SpecKit artifact files (spec.md, plan.md, tasks.md, constitution.md) |
| `UNKNOWN` | Fallback for unrecognized source types; triggers validation warning |

### PrivacyLabel

Controls how a record is classified for audit and optional caller-specified filtering.
Does **not** automatically restrict retrieval (clarification Q3).

| Value | Description |
|---|---|
| `PUBLIC` | Non-sensitive; safe to share or display without restriction |
| `INTERNAL` | Project-internal; appropriate for team or personal use |
| `PRIVATE` | Personal data; default for all records unless explicitly overridden |
| `CONFIDENTIAL` | Highly sensitive personal data (credentials, medical, financial) |

**Default**: `PRIVATE` — ingestion mappers must explicitly opt down to `INTERNAL` or `PUBLIC`.

### ProcessingStatus

Tracks pipeline progress for a SourceItem through ingestion stages.

| Value | Description |
|---|---|
| `PENDING` | Record ingested; not yet chunked |
| `CHUNKED` | SourceChunks created; not yet embedded |
| `EMBEDDED` | All chunks have embeddings; record is fully searchable |
| `FAILED` | An error occurred at any pipeline stage |

**Transitions**: PENDING → CHUNKED → EMBEDDED (happy path); any stage → FAILED on error.
**Initial value**: PENDING on first ingestion.

### RetrievalMode

Identifies how a SourceChunk was found in a RetrievalResult.

| Value | Description |
|---|---|
| `SEMANTIC` | Vector similarity search over embeddings |
| `EXACT` | Direct lookup by canonical_id, source_url, or metadata filter |
| `TEMPORAL` | Date-bounded activity query (weekly/monthly/yearly range) |
| `HYBRID` | Combined keyword, metadata, embedding, and reranking search |

---

## Entities

### SourceItem

The canonical normalized record for any ingested external document, event, or page.

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `source_type` | SourceType | ✅ | — | Which external system this record came from |
| `source_name` | str | ✅ | — | Human-readable name (e.g., repo name, notebook name, sender) |
| `canonical_id` | str | ✅ | — | Unique identifier within `source_type` namespace (e.g., `github:jeffjames/Jarvis#42`) |
| `source_url` | str | ✅ | — | Direct URL or path to the original record; local path if no URL exists |
| `body_text` | str | ✅ | — | Raw content as retrieved from source (may contain HTML/Markdown markup) |
| `retrieval_text` | str | ✅ | — | Normalized text for chunking and embedding (stripped markup, cleaned whitespace) |
| `created_at` | datetime | ✅ | — | Original creation timestamp from the source system (immutable after first ingestion) |
| `updated_at` | datetime | ✅ | — | Last update timestamp; set to re-ingestion time on upsert |
| `privacy_label` | PrivacyLabel | ✅ | `PRIVATE` | Classification label; defaults to PRIVATE if not set by mapper |
| `processing_status` | ProcessingStatus | ✅ | `PENDING` | Current pipeline stage |
| `deleted_at` | datetime \| None | ✅ | `None` | Set when soft-deleted; `None` means active |
| `project` | str \| None | | `None` | Repository or project name for filtering (e.g., "Jarvis") |
| `summary` | str \| None | | `None` | Human-readable one-paragraph description; populated during ingestion or by LLM |

**Identity**: `(source_type, canonical_id)` is the compound natural key for upsert.

**Upsert behavior**: On re-ingestion with matching `canonical_id`, all fields except
`canonical_id` and `created_at` are overwritten. `processing_status` resets to `PENDING`.
Associated SourceChunks are replaced.

**Soft delete**: Setting `deleted_at` marks the record as deleted. Retrieval layers exclude
soft-deleted records by default.

---

### SourceChunk

A text slice of a SourceItem produced during ingestion for embedding and retrieval.

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `chunk_id` | str | ✅ | — | Unique identifier for this chunk (e.g., `{canonical_id}::chunk::{index}`) |
| `parent_id` | str | ✅ | — | References `SourceItem.canonical_id` of the parent record |
| `chunk_index` | int | ✅ | — | Zero-based position of this chunk within the parent (0 = first) |
| `chunk_text` | str | ✅ | — | The text slice from `retrieval_text` |
| `char_count` | int | ✅ | — | Exact character count of `chunk_text`; MUST match `len(chunk_text)` |
| `embedding` | list[float] \| None | ✅ | `None` | Vector embedding; `None` until the embedding stage completes |

**Chunk size**: Default target 500–1500 characters. Hard maximum 2000 characters. Records
shorter than 500 characters are stored as a single chunk.

**Chunk ID convention**: `{parent_canonical_id}::chunk::{chunk_index}` (e.g.,
`github:Jarvis#42::chunk::0`).

**Replacement on upsert**: When the parent SourceItem is upserted, all existing SourceChunks
for that parent MUST be deleted and re-created from the updated `retrieval_text`.

---

### RetrievalResult

A search result returned by the retrieval layer, wrapping a SourceChunk with citation metadata.

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `chunk_id` | str | ✅ | — | References `SourceChunk.chunk_id` |
| `parent_id` | str | ✅ | — | References `SourceItem.canonical_id` |
| `source_url` | str | ✅ | — | Copied from parent SourceItem for citation without extra lookup |
| `source_type` | SourceType | ✅ | — | Copied from parent SourceItem for filtering and display |
| `chunk_text` | str | ✅ | — | The matched chunk text |
| `retrieval_score` | float | ✅ | — | Relevance score in [0.0, 1.0]; higher is more relevant |
| `retrieval_mode` | RetrievalMode | ✅ | — | How this result was found (SEMANTIC, EXACT, TEMPORAL, HYBRID) |

**No storage**: RetrievalResult is a transient response object; it is never persisted.

**Citation contract**: The fields `parent_id`, `source_url`, and `source_type` MUST always
be present so report generators can produce citations without additional lookups (SC-003).

---

### EvidenceRef

A citation record linking one or more claims in a generated report to their supporting sources.

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `claim_text` | str | ✅ | — | The exact claim or statement being cited |
| `source_ids` | list[str] | ✅ | — | One or more `SourceItem.canonical_id` values supporting this claim |
| `chunk_ids` | list[str] \| None | | `None` | Optional specific `SourceChunk.chunk_id` values for precise attribution |
| `report_id` | str | ✅ | — | Identifier of the report that contains this claim |

**Minimum attribution**: At least one `source_id` MUST be present. `chunk_ids` are optional
but recommended for semantic results to enable pinpoint citation.

**No storage** (initial): EvidenceRef is a report-generation artifact. Persistence is out of
scope for this feature; reports may embed EvidenceRefs inline.

---

## Entity Relationships

```
SourceItem (1) ──────── (many) SourceChunk
  canonical_id              parent_id → canonical_id

RetrievalResult (transient, wraps SourceChunk fields)
  parent_id → SourceItem.canonical_id
  chunk_id  → SourceChunk.chunk_id

EvidenceRef (report artifact, references SourceItems)
  source_ids[] → SourceItem.canonical_id
  chunk_ids[]  → SourceChunk.chunk_id
```

---

## Source Type Mapping

How each supported source maps to SourceItem fields:

| Source | source_type | canonical_id pattern | source_url | body_text source | project |
|---|---|---|---|---|---|
| GitHub issue | GITHUB | `github:{owner}/{repo}#issue:{number}` | Issue HTML URL | issue title + body | repo name |
| GitHub PR | GITHUB | `github:{owner}/{repo}#pr:{number}` | PR HTML URL | PR title + body | repo name |
| GitHub commit | GITHUB | `github:{owner}/{repo}#commit:{sha}` | Commit HTML URL | commit message | repo name |
| GitHub milestone | GITHUB | `github:{owner}/{repo}#milestone:{number}` | Milestone URL | milestone title + description | repo name |
| OneNote page | ONENOTE | `onenote:{notebook}:{section}:{page_id}` | Page URL (if available) | page HTML content | notebook name |
| Gmail message | EMAIL | `email:gmail:{message_id}` | Gmail URL | subject + body | None |
| Outlook message | EMAIL | `email:outlook:{message_id}` | Outlook URL | subject + body | None |
| Google Calendar event | CALENDAR | `calendar:google:{event_id}` | Event URL | title + description | None |
| Outlook Calendar event | CALENDAR | `calendar:outlook:{event_id}` | Event URL | title + description | None |
| SpecKit spec.md | SPECKIT | `speckit:{repo_relative_path}` | Relative file path | full file content | parent dir name |
| SpecKit plan.md | SPECKIT | `speckit:{repo_relative_path}` | Relative file path | full file content | parent dir name |
| SpecKit tasks.md | SPECKIT | `speckit:{repo_relative_path}` | Relative file path | full file content | parent dir name |
| SpecKit constitution.md | SPECKIT | `speckit:{repo_relative_path}` | Relative file path | full file content | parent dir name |

---

## Validation Rules (from spec)

- `source_type` MUST match a defined `SourceType` enum value; UNKNOWN is valid but triggers a warning.
- `canonical_id` MUST be a non-empty string.
- `privacy_label` defaults to `PRIVATE` if not supplied.
- `processing_status` defaults to `PENDING` on first ingestion.
- `deleted_at` MUST be `None` for active records.
- `char_count` on SourceChunk MUST equal `len(chunk_text)`.
- `char_count` MUST be ≤ 2000; records with chunks exceeding 2000 characters are invalid.
- `retrieval_score` MUST be in [0.0, 1.0].
- `source_ids` on EvidenceRef MUST contain at least one entry.
