# Feature Specification: Knowledge Model Foundation

**Feature Branch**: `001-knowledge-model`

**Created**: 2026-05-31

**Status**: Draft

**Input**: User description: "Define Jarvis's normalized internal data model with a canonical structure,
chunking of source ingestion, retrieval, and references back to sources. Define metadata conventions
and privacy/security labels. Acceptance has all GitHub, OneNote, email, calendar, and SpecKit files
mapping into the model."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Map Any Source Into Canonical Form (Priority: P1)

As the ingestion layer, I need a single canonical record shape that every data source can map into,
so that retrieval, reporting, and citation work the same way regardless of where data came from.

**Why this priority**: Without a shared canonical record, each source requires bespoke retrieval and
reporting logic. A unified model is the prerequisite for every downstream feature.

**Independent Test**: A developer can take a raw GitHub issue, a OneNote page, an email, a calendar
event, and a SpecKit spec file, and produce a SourceItem for each one with all required fields
populated — without writing source-specific query or report code.

**Acceptance Scenarios**:

1. **Given** a raw GitHub issue with title, body, URL, timestamps, and repo name, **When** the
   ingestion mapper runs, **Then** a SourceItem is produced with source_type=GITHUB, canonical_id,
   source_url, body_text, timestamps, project, and privacy_label all set.
2. **Given** a OneNote page with title, content, and notebook path, **When** the ingestion mapper
   runs, **Then** a SourceItem is produced with source_type=ONENOTE and all required fields set.
3. **Given** a Gmail message with subject, body, sender, and timestamp, **When** the ingestion
   mapper runs, **Then** a SourceItem is produced with source_type=EMAIL and all required fields.
4. **Given** a Google Calendar event with title, description, start/end times, and attendees,
   **When** the ingestion mapper runs, **Then** a SourceItem is produced with
   source_type=CALENDAR and all required fields.
5. **Given** a SpecKit spec.md file with feature name and content, **When** the ingestion mapper
   runs, **Then** a SourceItem is produced with source_type=SPECKIT and all required fields.

---

### User Story 2 - Chunk Long Sources for Retrieval (Priority: P2)

As the retrieval system, I need long source documents split into addressable chunks with back-
references to their parent SourceItem, so that semantic search can find relevant passages rather
than being forced to retrieve entire documents.

**Why this priority**: Many sources (emails, notes, specs) are too long for a single embedding.
Chunking is required for meaningful semantic search and precise citation.

**Independent Test**: A long OneNote page can be chunked into multiple SourceChunks, each with a
reference back to the parent SourceItem. A retrieval query returns the most relevant chunk, and
the chunk's parent reference resolves to the original page.

**Acceptance Scenarios**:

1. **Given** a SourceItem with body_text longer than the chunking threshold, **When** the chunker
   runs, **Then** multiple SourceChunks are produced, each with parent_id pointing to the
   SourceItem, a chunk_index for ordering, and the chunk's text slice.
2. **Given** a SourceItem short enough to fit in a single chunk, **When** the chunker runs,
   **Then** exactly one SourceChunk is produced.
3. **Given** a SourceChunk with a parent_id, **When** the parent is looked up, **Then** the
   original SourceItem is returned with all its metadata intact.

---

### User Story 3 - Retrieve Evidence With Source Citations (Priority: P3)

As the reporting system, I need retrieval results that carry enough citation metadata to attribute
every claim in a report back to a specific source record, so that reports are auditable and the
user can verify any statement.

**Why this priority**: Source citation is a core constitutional requirement (Article II). Without
citation-capable retrieval results, reports cannot comply with the constitution.

**Independent Test**: A semantic search query returns RetrievalResults where each result identifies
the matched SourceChunk, its parent SourceItem, the retrieval score, and the retrieval mode. A
report generator can produce an EvidenceRef for each claim without additional lookups.

**Acceptance Scenarios**:

1. **Given** a retrieval query, **When** results are returned, **Then** each RetrievalResult
   contains: the matched chunk text, chunk_id, parent source_id, source_url, source_type,
   retrieval_score, and retrieval_mode.
2. **Given** a generated report claim, **When** an EvidenceRef is created for it, **Then** the
   EvidenceRef links the claim to one or more source_ids and optionally to specific chunk_ids.
3. **Given** a report with EvidenceRefs, **When** the user views a claim, **Then** the source
   URL or reference is present and navigable.

---

### Edge Cases

- What happens when a source record has no body text (e.g., a calendar event with only a title)?
  The body_text field should accept an empty string; summary may substitute.
- How does the model handle sources that lack a canonical URL (e.g., a local SpecKit file)?
  A local file path or relative repo path is used as source_url.
- What if a SourceItem's source_type does not match any defined enum value?
  The record is rejected with a validation error; unmapped types are not silently stored.
- What if privacy_label is not set by the ingestion mapper?
  The default label PRIVATE is applied; ingestion must explicitly opt down to INTERNAL or PUBLIC.
- What happens when a SourceItem is re-ingested (same canonical_id, updated content)?
  The existing record is upserted: changed fields overwritten, canonical_id and created_at
  preserved, updated_at refreshed, and SourceChunks replaced to reflect updated content.
- What happens when chunking or embedding fails for a SourceItem?
  processing_status is set to FAILED; the record remains stored with whatever fields were
  successfully populated, and the failure is surfaced for operator review.
- What happens when a source record is deleted at its origin?
  The SourceItem and its chunks are soft-deleted via deleted_at; excluded from retrieval by
  default but retained for historical reports and citation audit trails.

## Clarifications

### Session 2026-05-31

- Q: When an already-stored SourceItem is re-ingested with the same `canonical_id`, what should happen? → A: Upsert — update the existing record in place (overwrite changed fields, preserve canonical_id).
- Q: Should `SourceItem` include a processing status field to track pipeline progress? → A: Yes — add `processing_status` to SourceItem with values PENDING, CHUNKED, EMBEDDED, FAILED.
- Q: Should the retrieval layer automatically filter SourceItems by `privacy_label`, or is privacy label metadata/audit only at this stage? → A: Metadata/audit only — labels are stored and filterable but retrieval does not enforce access rules automatically.
- Q: Should `SourceChunk` include a size field, and should the spec define a target chunk size range? → A: Yes — add `char_count` to SourceChunk and define a default target range of 500–1500 characters.
- Q: When a source record is deleted at its origin, how should the corresponding SourceItem be handled? → A: Soft delete — add `deleted_at` timestamp; deleted records excluded from retrieval by default but retained for audit and historical reports.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST define a SourceItem entity as the canonical normalized record for any
  ingested document, event, or page, with the following required fields: source_type, source_name,
  canonical_id, source_url, body_text, retrieval_text, created_at, updated_at, privacy_label,
  project, processing_status, and deleted_at (nullable; null means active). The entity MUST also
  define an optional metadata field (dict or None) for source-specific supplementary data such as
  email sender, calendar attendees, or GitHub labels that do not map to a dedicated top-level field.
- **FR-001a**: When a SourceItem with a matching `canonical_id` is ingested a second time, the
  system MUST upsert: update all changed fields in the existing record rather than creating a
  duplicate. The `canonical_id` and `created_at` fields MUST be preserved; `updated_at` MUST
  reflect the re-ingestion time. `processing_status` MUST reset to PENDING. Associated SourceChunks
  MUST be replaced to reflect updated content.
- **FR-001b**: The system MUST define a `processing_status` enumeration for SourceItem with values:
  PENDING (ingested, not yet chunked), CHUNKED (chunks created, not yet embedded), EMBEDDED (chunks
  have embeddings and are searchable), and FAILED (an error occurred at any pipeline stage). The
  initial status on first ingestion MUST be PENDING. The system MUST surface FAILED records so
  that operators can identify incomplete ingestion without scanning raw logs.
- **FR-001c**: When a source record is deleted at its origin, the corresponding SourceItem MUST be
  soft-deleted by setting `deleted_at` to the deletion timestamp. Soft-deleted records MUST be
  excluded from all retrieval queries by default. Callers MAY explicitly request soft-deleted
  records for audit or historical report purposes. SourceChunks of soft-deleted SourceItems MUST
  also be excluded from retrieval by default.
- **FR-002**: The system MUST define a SourceChunk entity representing a text slice of a SourceItem,
  with required fields: chunk_id, parent_id (references SourceItem.canonical_id), chunk_index,
  chunk_text, char_count, and embedding (nullable until embedded).
- **FR-002a**: The default target chunk size is 500–1500 characters. Chunks MUST NOT exceed 2000
  characters. Short source records that fall below 500 characters MAY be stored as a single chunk
  without splitting. The chunker MUST record the actual char_count on each SourceChunk so the
  model is self-describing and the chunker output is independently validatable.
- **FR-003**: The system MUST define a RetrievalResult entity wrapping a SourceChunk for search
  responses, with required fields: chunk_id, parent_id, source_url, source_type, chunk_text,
  retrieval_score, and retrieval_mode.
- **FR-004**: The system MUST define an EvidenceRef entity linking a report claim to source records,
  with required fields: claim_text, source_ids (list), chunk_ids (list, optional), and report_id.
- **FR-005**: The system MUST define a privacy_label enumeration with values: PUBLIC, INTERNAL,
  PRIVATE, and CONFIDENTIAL. PRIVATE MUST be the default when no label is explicitly set.
  privacy_label is stored for metadata, audit, and optional caller-specified filtering purposes;
  the retrieval layer MUST NOT automatically exclude records based on privacy_label. Callers MAY
  pass a privacy_label filter to retrieval queries, but enforcement is not automatic.
- **FR-006**: The system MUST define a source_type enumeration covering: GITHUB, ONENOTE, EMAIL,
  CALENDAR, and SPECKIT as minimum supported values, with an UNKNOWN fallback.
- **FR-007**: GitHub records (commits, issues, pull requests, discussions, and milestones) MUST each
  be mappable to a SourceItem with all required fields populated.
- **FR-008**: OneNote notebook pages MUST be mappable to a SourceItem with all required fields
  populated.
- **FR-009**: Email messages from Gmail or Outlook MUST be mappable to a SourceItem with all
  required fields populated.
- **FR-010**: Calendar events from Google Calendar or Outlook Calendar MUST be mappable to a
  SourceItem with all required fields populated.
- **FR-011**: SpecKit artifacts (spec.md, plan.md, tasks.md, constitution.md) MUST be mappable to a
  SourceItem with all required fields populated.
- **FR-012**: SourceItem MUST define a summary field (nullable). The field MAY be left unpopulated
  at ingestion time; it is populated during ingestion or by the LLM when a human-readable
  one-paragraph description of the record is available.
- **FR-013**: SourceItem MUST include a retrieval_text field containing normalized, embedding-ready
  text derived from body_text (stripped of markup, code blocks, etc.) used for chunking and search.
- **FR-014**: SourceItem MUST include an optional project field for repository or project name,
  allowing records to be filtered by project context.
- **FR-015**: All entities MUST have tests that validate required fields are present and that
  invalid records (missing required fields or unknown source_types) are rejected.

### Key Entities

- **SourceItem**: The canonical normalized record for any ingested external document, event, or page.
  Represents one logical unit of content: a GitHub issue, an email, a calendar event, a note page,
  or a spec file. Contains full provenance (source_url, source_type, canonical_id), body content
  (body_text), normalized retrieval content (retrieval_text), timestamps, project association,
  privacy label, optional summary, optional metadata dict for source-specific supplementary fields,
  processing_status tracking pipeline progress through PENDING → CHUNKED → EMBEDDED (or FAILED),
  and deleted_at for soft deletion (null means active; non-null means excluded from retrieval).
- **SourceChunk**: A sub-section of a SourceItem produced during ingestion for embedding and
  retrieval. Contains the chunk text, its character count (char_count), its position within the
  parent (chunk_index), and a reference back to the parent SourceItem via parent_id. Default target
  size is 500–1500 characters; hard maximum is 2000 characters. Holds the embedding vector once
  computed.
- **RetrievalResult**: A search result returned by the retrieval layer. Wraps a SourceChunk and
  augments it with retrieval metadata: score, mode (semantic, exact, temporal, hybrid), and enough
  citation data (source_url, source_type) for report generation without an additional lookup.
- **EvidenceRef**: A citation record linking one or more claims in a generated report to their
  supporting source records. Contains the claim text, a list of supporting source_ids, and optional
  chunk_ids for precise attribution.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All five source types (GitHub, OneNote, email, calendar, SpecKit) can be mapped to
  SourceItem without omitting any required field, verified by passing mapping tests for each type.
- **SC-002**: A retrieval result can be traced back to its originating source document via a single
  parent_id lookup, with no intermediate joins or extra queries required.
- **SC-003**: Reports can attribute claims to source records via EvidenceRef without additional
  database lookups beyond the fields already in RetrievalResult.
- **SC-004**: Invalid SourceItems (missing required fields or unrecognized source_type) are rejected
  with a clear validation error 100% of the time, not silently stored.
- **SC-005**: Privacy labels are present on 100% of stored SourceItems, defaulting to PRIVATE
  when not explicitly set by the mapper.
- **SC-006**: All required-field and mapping tests pass in CI with no API keys or external services
  needed (using fixture data for each source type).
- **SC-007**: FAILED SourceItems are queryable as a distinct set (filterable by processing_status),
  enabling an operator to list all records that did not complete ingestion without scanning logs.
- **SC-008**: All SourceChunks have a char_count that matches the actual length of their chunk_text,
  and no chunk exceeds 2000 characters, verified by chunking tests against fixture sources.
- **SC-009**: Soft-deleted SourceItems (deleted_at is set) do not appear in retrieval results by
  default; they are retrievable only when explicitly requested, verified by test.

## Assumptions

- Each supported source type has a stable identifier (e.g., issue number, page ID, message ID,
  event ID) suitable for use as canonical_id within its source_type namespace.
- The model is defined as pure data contracts, not tied to any specific storage backend; the
  persistence layer implements the model separately and is out of scope for this feature.
- Outlook and Gmail email are treated as the same EMAIL source_type; Calendar events from either
  provider map to CALENDAR. Source-specific supplementary data (e.g., sender, recipients,
  attendees, labels) lives in the optional SourceItem `metadata` dict field (defined in FR-001)
  rather than requiring separate source-type-specific entity types.
- body_text may contain raw markup (HTML, Markdown); retrieval_text is the cleaned version. Both
  are stored; only retrieval_text is used for chunking and embedding.
- SpecKit artifacts are identified by their file path within the repository; the canonical_id
  is derived from the relative file path.
- The initial model covers the five listed source types; additional source types (tasks, Slack,
  etc.) may be added later without breaking the schema by extending the source_type enumeration.
