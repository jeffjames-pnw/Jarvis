# Jarvis — AI Web Service

## What this is
A personal AI web service built as a learning platform for modern AI infrastructure:
FastAPI + LangGraph + ChromaDB + Docker + GitHub Actions + LangSmith + Anthropic API,
deployed on Render. The goal is a working foundation to build real agents on top of.

## Live deployment
- **Render**: https://jarvis-ooow.onrender.com
- **GitHub**: https://github.com/jeffjames-pnw/Jarvis
- **LangSmith**: project "jarvis" at smith.langchain.com

## Architecture decisions (with reasons)

| Decision | Choice | Why |
|---|---|---|
| Package manager | uv | Fast, modern, lockfile-based |
| LLM provider | Anthropic API (Claude) | Separate from claude.ai subscription; pay-per-token |
| Default model | claude-haiku-4-5-20251001 | Fast and cheap for dev; configurable via MODEL_NAME env var |
| Observability | LangSmith | Zero-config for LangGraph; just set env vars |
| Vector store | ChromaDB embedded PersistentClient | No separate service needed; upgradeable to HTTP client later |
| Deployment | Render (Starter plan) | Azure quota issues during setup; Docker-native, auto-deploys on push |
| Chat style | Non-streaming | Simpler for now; streaming can be added later |

## Tech stack mental model
- **Claude** — the LLM; the only thing that reasons
- **LangGraph** — orchestrates which nodes run in what order; manages shared state (messages list)
- **ChromaDB** — long-term semantic memory; queried before LLM calls to inject relevant context
- **LangSmith** — traces every graph execution; zero instrumentation required beyond env vars
- **MCP** — discovery and calling protocol for external tools; not magic context transport

Graph state is in-memory per request (ephemeral). ChromaDB is persistent across requests.
Each LLM call re-reads the full accumulated messages list — there is no persistent "understanding."

## Project structure
```
src/jarvis/
├── main.py               # FastAPI app factory; mounts all routers
├── api/
│   ├── routes.py         # GET / and GET /health
│   └── chat.py           # POST /chat → graph.ainvoke()
├── agents/
│   ├── graph.py          # LangGraph StateGraph compiled at startup
│   └── nodes.py          # call_model node (Claude call lives here)
├── core/
│   ├── config.py         # pydantic-settings; reads from .env
│   ├── llm.py            # ChatAnthropic factory (lru_cache singleton)
│   └── logging.py        # JSON formatter for structured stdout logs
├── memory/
│   └── chroma.py         # ChromaDB PersistentClient (wired up, not yet used in graph)
└── middleware/
    └── access.py         # Logs every request: method, path, status, duration_ms, client_ip
```

## Key conventions
- **Tests mock the LLM** — `patch("jarvis.api.chat.graph")` in test_chat.py so CI needs no API keys
- **Lint**: `uv run ruff check .` — rules E, F, I, UP; line length 100
- **Tests**: `uv run pytest` — asyncio_mode = auto
- **No secrets in any committed file** — ANTHROPIC_API_KEY and LANGSMITH_API_KEY set manually in Render dashboard; locally in .env (gitignored)
- **CI** — GitHub Actions: checkout@v6, setup-uv@v8.1.0 (pinned; v8+ removed floating major tags), runs `uv sync --all-extras` then ruff then pytest

## Environment variables
| Variable | Where set | Notes |
|---|---|---|
| ANTHROPIC_API_KEY | Render dashboard / .env | Never commit; rotated May 2026 |
| LANGSMITH_API_KEY | Render dashboard / .env | Never commit; rotated May 2026 |
| LANGSMITH_TRACING | render.yaml / .env | Set to `true` to enable |
| LANGSMITH_PROJECT | render.yaml / .env | "jarvis" |
| MODEL_NAME | render.yaml / .env | claude-haiku-4-5-20251001 |
| CHROMA_PATH | render.yaml / .env | ./chroma_data (gitignored) |

## Dev workflow
```bash
cp .env.example .env        # fill in API keys
uv sync --all-extras        # install all deps including dev
uv run uvicorn jarvis.main:app --reload   # local dev server at :8000
uv run pytest               # run tests (no API keys needed)
uv run ruff check .         # lint
git push origin main        # triggers CI + Render auto-deploy
```

## Current state — Phase 2 complete
- [x] Phase 1: FastAPI hello world, Docker, CI/CD, Render deployment, structured access logging
- [x] Phase 2: POST /chat backed by single-node LangGraph graph calling Claude via langchain-anthropic; ChromaDB wired up; LangSmith tracing enabled
- [x] Phase 3: Personal assistant — GitHub tools + OneNote ingestion into ChromaDB + ReAct agent
- [ ] Phase 4: Email (Gmail OAuth), conversation memory, scheduling

## Phase 3 — what was built
**Graph:** `create_react_agent` with 5 tools. Claude decides which to call based on the question.
**Tools:** `list_my_issues`, `list_my_prs`, `search_code`, `get_my_activity` (GitHub live API), `search_notes` (ChromaDB semantic search)
**Ingestion:** `POST /ingest/notes` pulls all OneNote pages via Microsoft Graph API, chunks them, upserts into ChromaDB collection "notes"
**OAuth setup:** Run `uv run python scripts/get_microsoft_token.py` once locally to get MICROSOFT_REFRESH_TOKEN

## Secrets required in Render dashboard
ANTHROPIC_API_KEY, LANGSMITH_API_KEY, GITHUB_TOKEN, MICROSOFT_CLIENT_ID, MICROSOFT_REFRESH_TOKEN

<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan
at specs/001-knowledge-model/plan.md
<!-- SPECKIT END -->
