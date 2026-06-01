---
description: "Task list for Knowledge Model Foundation"
---

# Tasks: Knowledge Model Foundation

**Input**: Design documents from `specs/001-knowledge-model/`

**Prerequisites**: plan.md ✅, spec.md ✅, data-model.md ✅, contracts/layer-contracts.md ✅,
research.md ✅, quickstart.md ✅

**Tests**: Included — FR-015 explicitly requires validation tests for all entities.

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Exact file paths included in all implementation tasks

## Path Conventions

- Source: `src/jarvis/models/` at repository root
- Tests: `tests/models/` at repository root

---

## Phase 1: Setup

**Purpose**: Create the package directories and stub files needed by all phases.

- [x] T001 Create `src/jarvis/models/__init__.py` (empty stub — exports added per story)
- [x] T002 Create `tests/models/__init__.py` (empty stub)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Enum definitions and shared test fixtures that ALL user stories depend on.
No user story implementation can begin until these are complete.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T003 [P] Define `SourceType` str-Enum (GITHUB, ONENOTE, EMAIL, CALENDAR, SPECKIT, UNKNOWN) in `src/jarvis/models/source_item.py`
- [x] T004 [P] Define `PrivacyLabel` str-Enum (PUBLIC, INTERNAL, PRIVATE, CONFIDENTIAL) in `src/jarvis/models/source_item.py` (field default=PRIVATE is set on SourceItem, not on the enum)
- [x] T005 [P] Define `ProcessingStatus` str-Enum (PENDING, CHUNKED, EMBEDDED, FAILED) in `src/jarvis/models/source_item.py`
- [x] T006 [P] Define `RetrievalMode` str-Enum (SEMANTIC, EXACT, TEMPORAL, HYBRID) in `src/jarvis/models/retrieval.py`
- [x] T007 Create `tests/models/conftest.py` with `@pytest.fixture` dicts for all 5 source types: GitHub issue, OneNote page, Gmail message, Google Calendar event, SpecKit spec.md file — each dict contains all required SourceItem fields pre-populated with valid sample data

**Checkpoint**: Enums importable and fixtures available — User Story phases can begin.

---

## Phase 3: User Story 1 — Map Any Source Into Canonical Form (Priority: P1) 🎯 MVP

**Goal**: `SourceItem` Pydantic model accepts all required fields, enforces defaults (PRIVATE,
PENDING, deleted_at=None), validates source_type against the enum, and all 5 source-type
fixture dicts produce valid SourceItem instances.

**Independent Test**: `uv run pytest tests/models/test_source_item.py -v` passes with no
external services. All 5 source-type fixture dicts map cleanly to SourceItem with zero
omitted required fields.

### Tests for User Story 1 ⚠️ Write FIRST — verify they FAIL before implementing SourceItem

- [x] T008 [P] [US1] Write test: SourceItem accepts all required fields from GitHub fixture in `tests/models/test_source_item.py`
- [x] T009 [P] [US1] Write test: SourceItem accepts all required fields from OneNote, EMAIL, CALENDAR, SPECKIT fixtures in `tests/models/test_source_item.py`
- [x] T010 [P] [US1] Write test: SourceItem defaults — privacy_label=PRIVATE, processing_status=PENDING, deleted_at=None when not supplied in `tests/models/test_source_item.py`
- [x] T011 [P] [US1] Write test: SourceItem raises ValidationError on missing required fields (canonical_id, source_url, body_text) in `tests/models/test_source_item.py`
- [x] T012 [P] [US1] Write test: SourceItem raises ValidationError for unknown source_type value in `tests/models/test_source_item.py`
- [x] T031 [P] [US1] Write test: SourceItem with `deleted_at` set is excluded from default retrieval results; passes when caller explicitly requests soft-deleted records in `tests/models/test_source_item.py` (covers SC-009 / FR-001c)
- [x] T032 [P] [US1] Write test: re-ingesting SourceItem with same `canonical_id` preserves `canonical_id` and `created_at`, updates `updated_at`, resets `processing_status` to PENDING in `tests/models/test_source_item.py` (covers FR-001a)
- [x] T033 [P] [US1] Write test: SourceItem with `processing_status=FAILED` is valid and identifiable via `processing_status` field filter in `tests/models/test_source_item.py` (covers SC-007 / FR-001b)

### Implementation for User Story 1

- [x] T013 [US1] Implement `SourceItem` Pydantic BaseModel with all fields from data-model.md (including `retrieval_text` as required, `metadata: dict | None = None` as optional) in `src/jarvis/models/source_item.py` (depends on T003–T005, T008–T012, T031–T033 failing)
- [x] T014 [US1] Export `SourceItem`, `SourceType`, `PrivacyLabel`, `ProcessingStatus` from `src/jarvis/models/__init__.py`

**Checkpoint**: `uv run pytest tests/models/test_source_item.py -v` passes — User Story 1
fully functional and independently testable.

---

## Phase 4: User Story 2 — Chunk Long Sources for Retrieval (Priority: P2)

**Goal**: `SourceChunk` Pydantic model with `char_count` field, validator that asserts
`char_count == len(chunk_text)`, hard maximum of 2000 characters, and `parent_id`
back-reference to `SourceItem.canonical_id`.

**Independent Test**: `uv run pytest tests/models/test_source_chunk.py -v` passes. A fixture
SourceItem can produce multiple valid SourceChunks. Parent reference resolves correctly.

### Tests for User Story 2 ⚠️ Write FIRST — verify they FAIL before implementing SourceChunk

- [x] T015 [P] [US2] Write test: SourceChunk accepts all required fields and char_count matches len(chunk_text) in `tests/models/test_source_chunk.py`
- [x] T016 [P] [US2] Write test: SourceChunk raises ValidationError when char_count != len(chunk_text) in `tests/models/test_source_chunk.py`
- [x] T017 [P] [US2] Write test: SourceChunk raises ValidationError when char_count > 2000 in `tests/models/test_source_chunk.py`
- [x] T018 [P] [US2] Write test: SourceChunk with embedding=None (default) and embedding=list[float] both valid in `tests/models/test_source_chunk.py`

### Implementation for User Story 2

- [x] T019 [US2] Implement `SourceChunk` Pydantic BaseModel with char_count field validator (`char_count == len(chunk_text)` and `char_count <= 2000`) in `src/jarvis/models/source_chunk.py` (depends on T015–T018 failing)
- [x] T020 [US2] Export `SourceChunk` from `src/jarvis/models/__init__.py`

**Checkpoint**: `uv run pytest tests/models/test_source_chunk.py -v` passes — User Stories 1
AND 2 independently functional.

---

## Phase 5: User Story 3 — Retrieve Evidence With Source Citations (Priority: P3)

**Goal**: `RetrievalResult` carries full citation metadata (chunk_id, parent_id, source_url,
source_type, retrieval_score in [0.0,1.0], retrieval_mode). `EvidenceRef` links report claims
to at least one source_id with optional chunk_ids.

**Independent Test**: `uv run pytest tests/models/test_retrieval.py tests/models/test_evidence.py -v`
passes. A RetrievalResult can be constructed from SourceChunk fields + citation data without
additional lookups. An EvidenceRef can be created from a RetrievalResult's parent_id.

### Tests for User Story 3 ⚠️ Write FIRST — verify they FAIL before implementing

- [x] T021 [P] [US3] Write test: RetrievalResult accepts all required fields; retrieval_score validates in [0.0, 1.0] in `tests/models/test_retrieval.py`
- [x] T022 [P] [US3] Write test: RetrievalResult raises ValidationError when retrieval_score outside [0.0, 1.0] in `tests/models/test_retrieval.py`
- [x] T023 [P] [US3] Write test: EvidenceRef accepts required fields with non-empty source_ids in `tests/models/test_evidence.py`
- [x] T024 [P] [US3] Write test: EvidenceRef raises ValidationError when source_ids is empty list in `tests/models/test_evidence.py`

### Implementation for User Story 3

- [x] T025 [US3] Implement `RetrievalResult` Pydantic BaseModel with retrieval_score validator in `src/jarvis/models/retrieval.py` (depends on T006, T021–T022 failing)
- [x] T026 [US3] Implement `EvidenceRef` Pydantic BaseModel with non-empty source_ids validator in `src/jarvis/models/evidence.py` (depends on T023–T024 failing)
- [x] T027 [US3] Export `RetrievalResult`, `RetrievalMode`, `EvidenceRef` from `src/jarvis/models/__init__.py`

**Checkpoint**: All user stories independently functional —
`uv run pytest tests/models/ -v` fully passes.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Lint, full regression check, and import smoke test.

- [x] T028 [P] Run `uv run ruff check src/jarvis/models/ tests/models/` and fix any E, F, I, UP violations (line length 100)
- [x] T029 [P] Run full test suite `uv run pytest` to confirm no regressions in `test_health.py` and `test_chat.py`
- [x] T030 Verify import smoke test: `from jarvis.models import SourceItem, SourceChunk, RetrievalResult, EvidenceRef, SourceType, PrivacyLabel, ProcessingStatus, RetrievalMode` works from a clean Python session

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Phase 2 completion
- **User Story 2 (Phase 4)**: Depends on Phase 2 completion (independent from US1)
- **User Story 3 (Phase 5)**: Depends on Phase 2 completion (independent from US1, US2)
- **Polish (Phase 6)**: Depends on all desired user stories complete

### User Story Dependencies

- **US1 (P1)**: Can start after Phase 2 — no dependency on US2 or US3
- **US2 (P2)**: Can start after Phase 2 — no dependency on US1 or US3
- **US3 (P3)**: Can start after Phase 2 — no dependency on US1 or US2

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD per FR-015)
- Enums (Phase 2) before models (Phase 3–5)
- Models before exports (__init__.py updates)
- All tests pass before moving to polish phase

### Parallel Opportunities

- T003, T004, T005, T006 — all enum definitions can run in parallel (different files/sections)
- T008–T012 — all US1 tests can run in parallel
- T015–T018 — all US2 tests can run in parallel
- T021–T024 — all US3 tests can run in parallel
- T028, T029 — lint and regression check can run in parallel
- US1, US2, US3 phases can proceed in parallel if separate developers

---

## Parallel Example: User Story 1

```bash
# Write all US1 tests in parallel:
Task T008: "Write test: SourceItem accepts GitHub fixture in tests/models/test_source_item.py"
Task T009: "Write test: SourceItem accepts OneNote/EMAIL/CALENDAR/SPECKIT fixtures"
Task T010: "Write test: SourceItem defaults (PRIVATE, PENDING, deleted_at=None)"
Task T011: "Write test: ValidationError on missing required fields"
Task T012: "Write test: ValidationError for unknown source_type"

# Then implement:
Task T013: "Implement SourceItem in src/jarvis/models/source_item.py"
Task T014: "Export from src/jarvis/models/__init__.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T002)
2. Complete Phase 2: Foundational enums + fixtures (T003–T007)
3. Complete Phase 3: User Story 1 — SourceItem (T008–T014)
4. **STOP and VALIDATE**: `uv run pytest tests/models/test_source_item.py -v`
5. Run `uv run ruff check src/jarvis/models/` — confirm lint passes

### Incremental Delivery

1. Phase 1–2 → Foundation ready
2. Phase 3 → SourceItem importable + tested → MVP (all 5 source types map into model)
3. Phase 4 → SourceChunk → chunking contract defined and tested
4. Phase 5 → RetrievalResult + EvidenceRef → full citation chain defined and tested
5. Phase 6 → Clean lint + full regression pass → ready for `/speckit-implement`

### Parallel Team Strategy

With multiple developers after Phase 2 completes:
- Developer A: User Story 1 (Phase 3)
- Developer B: User Story 2 (Phase 4)
- Developer C: User Story 3 (Phase 5)

---

## Notes

- `[P]` tasks = different files, no blocking dependencies — run in parallel
- `[Story]` label maps each task to its user story for traceability
- Tests MUST be written first and confirmed failing before each model is implemented
- All tasks are fixture-based — zero external services or API keys needed
- `uv run pytest tests/models/` is the validation command for this feature
- Ruff rules in effect: E, F, I, UP; line length 100
- **Deferred (C6/SC-002)**: US2 acceptance scenario 3 ("parent lookup resolves SourceItem") requires
  a storage lookup, not just a data contract. This is deferred to the persistence/retrieval layer
  feature; spec SC-002 will be validated there, not in model unit tests.
