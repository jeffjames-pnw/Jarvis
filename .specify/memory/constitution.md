<!--
SYNC IMPACT REPORT
==================
Version change: [placeholder] → 1.0.0
Modified principles: N/A — first population from docs/vision.md
Added sections:
  - Core Principles (8 Articles drawn from vision.md constitution section)
  - Architecture Standards (from vision.md architecture/retrieval/knowledge-model sections)
  - Development Standards (from vision.md product principles)
  - Governance
Removed sections: None
Templates requiring updates:
  ✅ .specify/memory/constitution.md — populated from docs/vision.md
  ✅ .specify/templates/plan-template.md — Constitution Check gate placeholder aligns with
     the 8 principles; filled per-feature by /speckit-plan, no structural change needed
  ✅ .specify/templates/spec-template.md — no constitution-specific sections; no change needed
  ✅ .specify/templates/tasks-template.md — observability and testing tasks align with
     Principle VI; layer-separation tasks align with Principle III; no change needed
Follow-up TODOs: None; all placeholders resolved.
-->

# Jarvis Constitution

## Core Principles

### I. Read-First Personal Intelligence

Jarvis is a personal intelligence system before it is an automation system. All new
data-source integrations MUST start read-only unless a specification explicitly justifies
write access, safety controls, confirmation flows, and audit logging.

**Rationale**: Premature write access introduces irreversible side effects before the system
has proven it understands context. Read-only is the safe default; write access is a named
upgrade requiring deliberate design.

### II. Source-Grounded Answers

Jarvis MUST provide source-grounded outputs whenever it summarizes private data. Reports,
dashboards, and strategic summaries MUST preserve links or references back to the underlying
source records where technically possible. Answers MUST NOT state conclusions without citing
supporting evidence.

**Rationale**: Private personal data is contextually rich; ungrounded summaries lose that
context and erode trust. Source links allow the user to verify, explore, and correct.

### III. Ingestion Is Separate From Answering

Connectors, ingestion, retrieval, agents, and reporting MUST remain separate architectural
layers. Agent logic MUST NOT directly own data fetching, normalization, embedding, or
persistence responsibilities. This boundary is non-negotiable and governs every new feature
design.

**Rationale**: Mixed responsibilities produce untestable, fragile code. Layered separation
allows each concern to be independently tested, replaced, and observed.

### IV. Durable Project Memory

Important project intent MUST live in repository files, not only in chat history. SpecKit
specs, plans, tasks, project notes, and architecture decisions are first-class Jarvis data
sources. Work that exists only in a transient session is considered lost.

**Rationale**: AI sessions are ephemeral. Repository files survive context loss, session
boundaries, and tool changes. Durable intent enables continuity across all of these.

### V. Privacy and Least Privilege

Jarvis MUST request the narrowest practical permissions for each data source. Secrets MUST
never be committed to version control. Private data MUST be labeled, traceable, and handled
with explicit boundaries between local development, test data, and production-like personal
data.

**Rationale**: Personal data (email, calendar, notes) is sensitive. Least-privilege limits
the blast radius of credential exposure and keeps the system auditable.

### VI. Observable and Testable AI Behavior

Agent runs, retrieval decisions, tool calls, generated reports, and failures MUST be
observable via tracing and logging. New features MUST include tests or evals appropriate to
their risk: unit tests for deterministic logic, retrieval tests for search behavior, and
scenario evals for report quality.

**Rationale**: AI behavior is non-deterministic. Without traces and evals, regressions and
hallucinations are invisible. Observability is not optional polish — it is a correctness
requirement.

### VII. Small Demoable Passes

Work MUST be organized into small, demoable implementation passes. Each pass SHOULD produce
a visible capability, a learning outcome, and a portfolio or interview story. Large,
non-demonstrable changes MUST be broken down before implementation begins.

**Rationale**: Small passes validate assumptions early, produce shareable artifacts, and
prevent wasted work on features built on incorrect foundations.

### VIII. Human Control Over Actions

Jarvis MAY recommend actions, draft outputs, and summarize commitments, but it MUST NOT
send emails, modify calendars, change issues, or update external systems without explicit
user confirmation and a logged action trail.

**Rationale**: The cost of an unwanted automated action (sent email, modified issue,
deleted event) exceeds the cost of a confirmation prompt. Human control is preserved until
write-safety is explicitly designed and audited.

## Architecture Standards

The Jarvis architecture MUST maintain the following layer separation. Each layer has exactly
one responsibility and MUST NOT absorb the responsibilities of adjacent layers:

- `connectors/` — fetch raw data from external systems (GitHub, OneNote, Gmail, Calendar)
- `ingestion/` — normalize, chunk, embed, and upsert data into the knowledge store
- `retrieval/` — perform exact, semantic, temporal, and hybrid search
- `agents/` — reason, plan, and call tools using retrieved evidence
- `reports/` — generate structured, cited, user-facing outputs
- `evals/` — test retrieval quality, answer quality, source citation, and agent behavior
- `observability/` — trace requests, retrieval decisions, tool calls, and report generation

The knowledge model MUST normalize external data into a shared internal record containing:
source metadata, timestamps, canonical IDs, source URLs, body text, summaries, embeddings,
and security labels. The system MUST distinguish between raw source records, normalized
records, chunks, embeddings, retrieval results, cited report evidence, and generated
summaries. New data sources MUST map cleanly into this model before they can be used in
retrieval or reporting.

Retrieval MUST support four modes: exact/live lookup (API calls), semantic lookup (vector
search), temporal/activity lookup (date-bounded timelines), and hybrid lookup (combining
keyword, metadata, embeddings, reranking, and source weighting).

## Development Standards

The following standards govern how Jarvis features are designed and built:

1. **Synthesize before automating.** A new feature SHOULD demonstrate synthesis of existing
   data before adding new automation. Automation layers are built on top of proven synthesis.
2. **Cite sources.** Every user-facing output that draws on private data MUST include
   traceable source references, not just conclusions.
3. **Prefer read-only access.** Write access MUST be explicitly justified per integration
   with a documented rationale, safety design, and confirmation workflow (see Principle VIII).
4. **Expose knowns and unknowns.** Jarvis SHOULD surface what it knows, what it does not
   know, and where answers came from — including missing-data warnings rather than guessing.
5. **Produce durable outputs.** Reports, summaries, dashboards, and project memory MUST be
   persisted to files or storage, not left only in transient responses.
6. **Build in small passes.** Each implementation pass MUST target a single demonstrable
   scenario, completing and validating it before the next pass begins. Pass order follows
   `docs/vision.md` implementation pass list unless a spec explicitly reorders.

## Governance

This constitution supersedes all other practices and conventions for the Jarvis project.
Amendments require:

1. A written rationale documented in the pull request or accompanying spec.
2. An update to `LAST_AMENDED_DATE` and a version bump per semantic versioning:
   - **MAJOR**: removal or redefinition of a principle or architectural layer
   - **MINOR**: addition of a new principle, new section, or materially expanded guidance
   - **PATCH**: clarifications, wording corrections, or non-semantic refinements
3. A review of all spec, plan, and task templates for alignment with any changed principles
   before the amendment is merged.

All feature specs MUST include a Constitution Check gate in their implementation plan,
verifying compliance with the eight principles above before Phase 0 research begins. The
gate MUST be re-checked after Phase 1 design before implementation starts.

**Version**: 1.0.0 | **Ratified**: 2026-05-31 | **Last Amended**: 2026-05-31
