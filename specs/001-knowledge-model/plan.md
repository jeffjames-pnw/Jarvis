# Implementation Plan: Knowledge Model Foundation

**Branch**: `001-knowledge-model` | **Date**: 2026-05-31 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-knowledge-model/spec.md`

## Summary

Define Jarvis's normalized internal data model as a `src/jarvis/models/` subpackage containing
four Pydantic v2 entities (SourceItem, SourceChunk, RetrievalResult, EvidenceRef) plus four
supporting enumerations (SourceType, PrivacyLabel, ProcessingStatus, RetrievalMode). The model
establishes the shared contract between the ingestion, retrieval, agents, and reporting layers.
All five supported source types (GitHub, OneNote, email, calendar, SpecKit) must map cleanly
into SourceItem. Unit tests validate all required fields, enum constraints, upsert semantics,
chunk size rules, soft-delete behavior, and source-type mappings using fixture data only (no API
keys required).

## Technical Context

**Language/Version**: Python 3.11+ (existing project)

**Primary Dependencies**: Pydantic v2 (already in stack via `pydantic_settings`), pytest
(existing test runner via `uv run pytest`)

**Storage**: N/A — this feature defines data contracts only; the persistence layer is out of scope

**Testing**: pytest via `uv run pytest`; asyncio_mode = auto (existing pytest config)

**Target Platform**: Linux server (Render/Docker, existing deployment target)

**Project Type**: Library module within existing FastAPI web-service

**Performance Goals**: Model instantiation and validation < 1ms per record (pure Python in-memory)

**Constraints**: All tests must pass in CI with no API keys and no external services; all test
data is fixture-based

**Scale/Scope**: 4 entity types, 4 enumeration types, ~22 total fields across all entities

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design — all gates still pass.*

| Principle | Status | Notes |
|---|---|---|
| I. Read-First Personal Intelligence | ✅ Pass | Pure data model definition; no external write access of any kind |
| II. Source-Grounded Answers | ✅ Pass | `source_url` and `canonical_id` are required fields; citation is built into the model |
| III. Ingestion Separate From Answering | ✅ Pass | This feature IS the contract that enforces layer separation; `jarvis.models` is the neutral import point for all layers |
| IV. Durable Project Memory | ✅ Pass | Model definitions are committed to the repository in `src/jarvis/models/`; spec and plan documented in `specs/` |
| V. Privacy and Least Privilege | ✅ Pass | `privacy_label` is a required field defaulting to `PRIVATE`; no external credentials needed |
| VI. Observable and Testable | ✅ Pass | `processing_status` field enables pipeline observability; FR-015 mandates validation tests |
| VII. Small Demoable Passes | ✅ Pass | This is Pass 1 of the vision.md implementation pass list; deliverable is a working importable model with passing tests |
| VIII. Human Control Over Actions | ✅ Pass | No external system modifications; read-only data contract definition |

**No violations. Complexity Tracking section not required.**

## Project Structure

### Documentation (this feature)

```text
specs/001-knowledge-model/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output — full field specifications
├── quickstart.md        # Phase 1 output — how to use the model
├── contracts/
│   └── layer-contracts.md  # Phase 1 output — inter-layer type contracts
└── tasks.md             # Phase 2 output (/speckit-tasks command)
```

### Source Code (repository root)

```text
src/jarvis/
├── models/                  # NEW subpackage
│   ├── __init__.py          # re-exports all public types
│   ├── source_item.py       # SourceItem, SourceType, PrivacyLabel, ProcessingStatus
│   ├── source_chunk.py      # SourceChunk
│   ├── retrieval.py         # RetrievalResult, RetrievalMode
│   └── evidence.py          # EvidenceRef
├── api/                     # existing — unchanged
├── agents/                  # existing — unchanged
├── core/                    # existing — unchanged
├── ingest/                  # existing — will import from models/ in a future feature
├── memory/                  # existing — will import from models/ in a future feature
└── middleware/              # existing — unchanged

tests/
├── models/                  # NEW test subpackage
│   ├── __init__.py
│   ├── conftest.py          # shared fixtures for all source types
│   ├── test_source_item.py  # SourceItem validation, upsert semantics, soft delete
│   ├── test_source_chunk.py # SourceChunk validation, char_count, chunk size rules
│   ├── test_retrieval.py    # RetrievalResult validation, score range
│   └── test_evidence.py     # EvidenceRef validation, source_ids required
├── test_health.py           # existing — unchanged
└── test_chat.py             # existing — unchanged
```

**Structure Decision**: Single-project layout under `src/jarvis/`. New `models/` subpackage
follows the same pattern as existing subpackages (`api/`, `agents/`, `core/`, `ingest/`,
`memory/`). Test coverage lives in `tests/models/` to mirror source structure.
