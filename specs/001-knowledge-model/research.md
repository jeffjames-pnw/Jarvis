# Research: Knowledge Model Foundation

**Feature**: 001-knowledge-model
**Date**: 2026-05-31
**Branch**: 001-knowledge-model

## Summary of Decisions

All technical choices below are resolved from the existing project stack (CLAUDE.md, config.py,
chroma.py) plus standard Python best practices. No external research was required — the stack
is already established.

---

## Decision 1: Data Model Library

**Decision**: Pydantic v2 `BaseModel` for all four entities (SourceItem, SourceChunk,
RetrievalResult, EvidenceRef).

**Rationale**: Pydantic is already in the project (`pydantic_settings.BaseSettings` in
`core/config.py`). FastAPI, which Jarvis uses, natively serializes Pydantic models. Pydantic v2
provides field-level validation, default factories, JSON serialization, and clear error messages
out of the box — all needed by FR-015 (validation errors on invalid records).

**Alternatives considered**:
- Python `dataclasses`: No built-in validation; would require manual validators to satisfy FR-015.
- `attrs`: Not in the existing stack; no benefit over Pydantic here.
- Plain `TypedDict`: No runtime validation at all.

---

## Decision 2: Enum Pattern

**Decision**: Python `str, Enum` subclasses for `SourceType`, `PrivacyLabel`,
`ProcessingStatus`, and `RetrievalMode`.

**Rationale**: `str` Enums serialize to plain strings in JSON without extra configuration,
which ChromaDB requires for document metadata (ChromaDB metadata values must be str/int/float).
Pydantic v2 validates `str` Enum fields by value, producing clear errors on invalid values.

**Alternatives considered**:
- `IntEnum`: Numeric IDs are less readable in storage and logs.
- Plain string constants: No type safety; invalid values silently accepted.

---

## Decision 3: Nullable Fields

**Decision**: `Optional[T] = None` (or `T | None = None` in Python 3.10+ syntax) for all
nullable fields: `deleted_at`, `embedding`, `summary`, `project`, `char_count` on chunk.

**Rationale**: Pydantic v2 treats `Optional[T]` as `T | None` and validates correctly. `None`
semantics are explicit: `deleted_at=None` means active; `deleted_at=<datetime>` means soft-deleted.

---

## Decision 4: Upsert Identity Keys

**Decision**: `canonical_id` is a plain `str` field. Uniqueness across re-ingestion is
enforced by the ingestion layer (not the model itself). The model documents `created_at` as
the immutable original timestamp and `updated_at` as the mutable re-ingestion timestamp.

**Rationale**: The model defines contracts, not persistence invariants. The spec (FR-001c) places
upsert responsibility on the ingestion layer. Making the model enforce immutability (e.g., via
`model_config = ConfigDict(frozen=True)`) would prevent legitimate in-memory mutation during
processing.

---

## Decision 5: Module Placement

**Decision**: New `src/jarvis/models/` subpackage with one file per entity group:
`source_item.py` (SourceItem + enums), `source_chunk.py` (SourceChunk), `retrieval.py`
(RetrievalResult + RetrievalMode), `evidence.py` (EvidenceRef).

**Rationale**: The existing project uses subpackages per concern (`api/`, `agents/`, `core/`,
`ingest/`, `memory/`). Adding `models/` follows the same pattern. Splitting by entity group
keeps files small and avoids circular imports when ingestion, retrieval, and reporting all
import from `models/`.

**Alternatives considered**:
- Single `models.py` file: Gets unwieldy as the model grows; imports become ambiguous.
- Placing models inside `ingest/` or `memory/`: Violates Principle III (ingestion must not own
  the shared contract; other layers import it too).

---

## Decision 6: Test Strategy

**Decision**: Unit tests in `tests/models/` using pytest fixtures with hardcoded sample data
for each source type. No external services, API keys, or database connections needed.

**Rationale**: FR-015 and SC-006 require tests to pass in CI without API keys. Pydantic model
tests are pure Python validation tests — create a model instance from a dict, assert fields are
set correctly, assert invalid inputs raise `ValidationError`. No mocking needed.

**Test fixture approach**: One conftest.py per test module with `@pytest.fixture` returning
sample dicts for each source type (GitHub issue, OneNote page, email, calendar event, SpecKit
file). Tests import fixture data and construct model instances.

---

## Resolved Unknowns

All Technical Context fields from the plan template are resolved:

| Field | Value |
|---|---|
| Language/Version | Python 3.11+ (existing project) |
| Primary Dependencies | Pydantic v2 (already in stack), pytest (existing test runner) |
| Storage | N/A — model definition only; storage backend is out of scope |
| Testing | pytest via `uv run pytest` |
| Target Platform | Linux server (Render/Docker, existing deployment) |
| Project Type | Library module within existing FastAPI web-service |
| Performance Goals | Model instantiation and validation < 1ms per record (pure Python) |
| Constraints | CI must pass with no API keys; all tests use fixture data |
| Scale/Scope | 4 entity types, ~22 fields total across all entities |
