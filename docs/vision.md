# Jarvis Vision

Jarvis is my personal AI operating system: a private, read-first agentic service that helps me understand my work, notes, plans, commitments, and opportunities across the tools where my life and projects actually happen.

Jarvis should help me answer three recurring questions:

1. **Progress** — What did I work on this week, month, quarter, or year? What changed across my projects?
2. **Strategy** — What ideas, decisions, risks, opportunities, and open questions have emerged from my notes and project activity?
3. **Dashboard** — What needs my attention now? What deadlines are near? Who is waiting on me? What should I prioritize next?

Jarvis is also a learning vehicle. It should teach me modern AI application development through practical implementation of:

* LLM service design
* agent orchestration
* structured retrieval
* vector search
* external data connectors
* model-context-protocol-style tool access
* observability
* evaluation
* privacy and security controls

Jarvis should begin as a read-only intelligence layer. It may later gain write capabilities, but only after explicit design, safety constraints, auditability, and user confirmation workflows are in place.

## Target Data Sources

Initial and planned sources include:

* GitHub repositories, commits, issues, pull requests, discussions, milestones, and projects
* OneNote notebooks and pages
* Outlook and Gmail email
* Outlook and Google Calendar
* task systems
* SpecKit project specifications, plans, tasks, and constitutions
* local project documentation

## Product Principles

1. Jarvis should synthesize before it automates.
2. Jarvis should cite its sources.
3. Jarvis should separate ingestion from reasoning.
4. Jarvis should prefer read-only access until write access is explicitly justified.
5. Jarvis should expose what it knows, what it does not know, and where answers came from.
6. Jarvis should produce durable outputs: reports, summaries, dashboards, and project memory.
7. Jarvis should be built in small, inspectable, demoable passes.

## Core Architecture

Jarvis should separate responsibilities into clear layers:

* `connectors/` fetch data from external systems
* `ingestion/` normalize, chunk, embed, and upsert data
* `retrieval/` perform exact, semantic, temporal, and hybrid search
* `agents/` reason, plan, and call tools
* `reports/` generate structured user-facing outputs
* `evals/` test retrieval quality, answer quality, source citation, and agent behavior
* `observability/` trace requests, retrieval decisions, tool calls, and report generation

## Retrieval Model

Jarvis should support multiple lookup modes:

1. **Exact/live lookup** — current source-of-truth calls to APIs such as GitHub, Gmail, Outlook, or Calendar.
2. **Semantic lookup** — vector search over notes, specs, emails, issues, and project documents.
3. **Temporal/activity lookup** — date-bounded timelines for weekly, monthly, quarterly, and yearly reporting.
4. **Hybrid lookup** — combining keyword search, metadata filters, embeddings, reranking, and source weighting.

## Knowledge Model

Jarvis should normalize external data into a shared internal model with source metadata, timestamps, canonical IDs, source URLs, body text, summaries, embeddings, and security labels.

The system should distinguish between:

* raw source records
* normalized records
* chunks
* embeddings
* retrieval results
* cited report evidence
* generated summaries

## Initial Success Scenario

The first meaningful end-to-end scenario is:

> “Generate a weekly progress report for my projects using GitHub activity, OneNote notes, tasks, and SpecKit specs. Group the report by project, cite sources, identify decisions and open questions, and propose priorities for next week.”

This scenario should drive the first implementation milestones because it exercises ingestion, retrieval, temporal filtering, summarization, citation, reporting, and observability.



# Jarvis Constitution

## Article I — Read-First Personal Intelligence

Jarvis is a personal intelligence system before it is an automation system. All new data-source integrations must start read-only unless a specification explicitly justifies write access, safety controls, confirmation flows, and audit logging.

## Article II — Source-Grounded Answers

Jarvis must provide source-grounded outputs whenever it summarizes private data. Reports, dashboards, and strategic summaries must preserve links or references back to the underlying source records where technically possible.

## Article III — Ingestion Is Separate From Answering

Connectors, ingestion, retrieval, agents, and reporting must remain separate architectural layers. Agent logic must not directly own data fetching, normalization, embedding, or persistence responsibilities.

## Article IV — Durable Project Memory

Important project intent must live in repository files, not only in chat history. SpecKit specs, plans, tasks, project notes, and architecture decisions are first-class Jarvis data sources.

## Article V — Privacy and Least Privilege

Jarvis must request the narrowest practical permissions for each source. Secrets must never be committed. Private data must be labeled, traceable, and handled with explicit boundaries between local development, test data, and production-like personal data.

## Article VI — Observable and Testable AI Behavior

Agent runs, retrieval decisions, tool calls, generated reports, and failures must be observable. New features must include tests or evals appropriate to their risk: unit tests for deterministic logic, retrieval tests for search behavior, and scenario evals for report quality.

## Article VII — Small Demoable Passes

Work must be organized into small, demoable implementation passes. Each pass should produce a visible capability, a learning outcome, and a portfolio/interview story.

## Article VIII — Human Control Over Actions

Jarvis may recommend actions, draft outputs, and summarize commitments, but it must not send emails, modify calendars, change issues, or update external systems without explicit user confirmation and a logged action trail.


# Jarvis SpecKit Implementation Passes

## Pass 0 — SpecKit Reconstitution

Goal: Recreate durable project context after losing Claude session context.

Spec:

* Add `vision.md`
* Add `.specify/memory/constitution.md`
* Add initial project architecture notes
* Add source inventory
* Add current-state inventory of existing code

Acceptance Criteria:

* Claude Code can explain the project purpose from files alone
* Constitution exists and governs future specs
* Existing code is mapped to intended architecture

## Pass 1 — Knowledge Model Foundation

Goal: Define Jarvis’s normalized internal data model.

Spec:

* Create canonical `SourceItem`
* Create `SourceChunk`
* Create `RetrievalResult`
* Create `EvidenceRef`
* Define source metadata conventions
* Define privacy/security labels

Acceptance Criteria:

* GitHub, OneNote, email, tasks, and SpecKit files can all map into the model
* Tests validate required fields
* Model supports source URL, timestamps, project, scenario, and citation metadata

## Pass 2 — SpecKit as a Data Source

Goal: Let Jarvis ingest its own specs, plans, tasks, and constitution.

Spec:

* Add connector for local `/specs/**`
* Parse `spec.md`, `plan.md`, `tasks.md`, and constitution files
* Extract feature name, scenario, acceptance criteria, tasks, and status
* Make SpecKit artifacts searchable and reportable

Acceptance Criteria:

* Jarvis can answer “what specs exist?”
* Jarvis can summarize current implementation plans
* Jarvis can include SpecKit tasks in progress reports

## Pass 3 — GitHub Activity Timeline

Goal: Build a reliable project activity timeline from GitHub.

Spec:

* Ingest issues, PRs, commits, milestones, and project metadata
* Normalize GitHub records into `SourceItem`
* Support date-bounded queries
* Link activity back to source URLs

Acceptance Criteria:

* Jarvis can retrieve GitHub activity for a week/month
* Reports include issue/PR/commit citations
* GitHub data is read-only

## Pass 4 — Retrieval Foundation

Goal: Implement layered retrieval.

Spec:

* Exact lookup by source ID, URL, date, and project
* Semantic search using embeddings/vector store
* Temporal filtering for weekly/monthly/yearly reporting
* Hybrid retrieval combining metadata and semantic similarity

Acceptance Criteria:

* Retrieval tests cover exact, semantic, and temporal queries
* Search results include source, score, timestamp, and citation reference
* Report generation can request evidence by timeframe and project

## Pass 5 — Weekly Progress Report

Goal: Produce the first end-to-end Jarvis report.

Spec:

* Generate weekly report from GitHub + SpecKit data first
* Later add OneNote/tasks/email
* Group by project
* Identify completed work, active work, blockers, decisions, and next priorities
* Include citations

Acceptance Criteria:

* Endpoint or CLI command generates report for a date range
* Output is structured Markdown
* Every major claim has supporting evidence
* Run is observable through tracing/logging

## Pass 6 — OneNote Strategic Notes Retrieval

Goal: Support strategy synthesis from notes.

Spec:

* Ingest OneNote pages
* Chunk and embed long notes
* Retrieve notes by project, topic, and timeframe
* Summarize decisions, opportunities, risks, and open questions

Acceptance Criteria:

* Jarvis can summarize strategy notes for a project
* Summaries distinguish facts, decisions, ideas, and questions
* Notes are cited back to notebook/page where possible

## Pass 7 — Personal Dashboard

Goal: Create a forward-looking dashboard.

Spec:

* Combine calendar, tasks, GitHub stale items, and recent notes
* Identify deadlines, waiting-on-me items, and suggested priorities
* Keep write actions disabled

Acceptance Criteria:

* Dashboard answers “what needs my attention?”
* Items are grouped by urgency and project
* Recommendations cite evidence

## Pass 8 — Agent Quality and Evals

Goal: Make Jarvis trustworthy and interview-ready.

Spec:

* Add scenario evals for weekly report, strategy summary, and dashboard
* Add retrieval regression tests
* Add hallucination/citation checks
* Add trace summaries

Acceptance Criteria:

* Eval suite runs locally and in CI
* Known prompts have expected source coverage
* Reports expose missing-data warnings rather than guessing
