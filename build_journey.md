# build_journey.md — Palantir Foundry Operational Decision Platform

The live decision log for this build. Public. In the repo.  
Every significant decision, problem encountered, and lesson learned goes here.

---

## Entry Log

| Phase | Status | Date | Notes |
|---|---|---|---|
| Planning | Complete | 2026-06-18 | All five planning files produced. GitHub-ready folder packaged. |
| Phase 0 — Setup | Complete | 2026-06-19 | Local git repo only (no GitHub remote yet, by user choice). Backend uses `uv` not pip. |
| Phase 1 — Data Foundation | Complete | 2026-06-19 | All GET routes verified live against seeded SQLite DB. |
| Phase 2 — OpsGraph AI | Pending | — | |
| Phase 3 — DecisionRoom AI | Pending | — | |
| Phase 4 — MissionBrief AI | Pending | — | |
| Phase 5 — Track A HTML Demo | Pending | — | |
| Phase 6 — Containerization + Deploy + Review | Pending | — | Folded Phase 7 tasks in |

---

## Planning Session Decisions

### DECISION — Build all three demos in one repo

**Decision:** OpsGraph AI, DecisionRoom AI, and MissionBrief AI are built as modules in a single repo (`palantir-foundry-decision-platform`), not as three separate repos.

**Reason:** OpsGraph creates the data foundation (objects, links, events) that DecisionRoom and MissionBrief consume. Splitting into three repos would require duplicating the Ontology layer and seed data, create sync overhead, and weaken the portfolio narrative. One repo tells a cleaner story: three capability layers on a shared foundation.

---

### DECISION — Backend framework: FastAPI

**Decision:** FastAPI over Flask, Django, or Express.

**Reason:** Native async fits the AI call pattern (non-blocking Anthropic SDK calls). Pydantic v2 is a first-class citizen, so request/response validation is free. Auto-generated `/docs` endpoint makes the API immediately inspectable without a client. Flask was considered but lacks native async; Express was ruled out to keep the AI ecosystem in Python.

---

### DECISION — Database: SQLite

**Decision:** SQLite over PostgreSQL, MongoDB, or any managed DB.

**Reason:** Three modules share one DB with straightforward relational data. No concurrent write load, no need for managed infra. Render supports SQLite on persistent disk. Keeps the build lean — no DB service to provision, no connection string complexity. Upgrade path to PostgreSQL is a config change if the project grows.

---

### DECISION — Frontend: React/Vite + D3

**Decision:** React 18 with Vite for the application shell; D3 v7 for the dependency graph.

**Reason:** React's component model maps cleanly to three independent module panels. Vite is fast to scaffold and deploy. D3 is chosen specifically for the dependency graph — a force-directed graph that responds to node selection is the right visualization for an Ontology. No abstraction layer (React Flow, Cytoscape) is needed at this scale; D3 direct gives full control over node styling and interaction.

---

### DECISION — AI model split: Sonnet for reasoning, Haiku for summarization

**Decision:** `claude-sonnet-4-6` for impact analysis and scenario recommendation; `claude-haiku-4-5-20251001` for briefing generation and action rationale.

**Reason:** Impact analysis and decision recommendation require multi-object reasoning and structured tradeoff explanation — tasks where response quality matters and Sonnet's reasoning depth justifies the cost. Briefing generation and action rationale are structured data → natural language tasks with narrow output requirements; Haiku is faster, cheaper, and sufficient. Not every project needs two models — this one does because the task complexity profiles are genuinely different.

---

### DECISION — Error handling: two-path model with exception queue

**Decision:** All three modules implement the same two-path error handling: automated recovery (retry → degraded mode → low-confidence flag) then human routing (exception queue entry with full context).

**Reason:** Silent AI failures are the worst outcome for an ops tool. The two-path model ensures every failure either recovers automatically or surfaces explicitly to a human. The exception queue is the same queue that surfaces business anomalies — one place, one interface, one mental model for the operator.

---

### DECISION — Containerization: Docker Compose for orchestration

**Decision:** `backend/Dockerfile` + `docker-compose.yml` at repo root. Backend and frontend orchestrated as services.

**Reason:** Deploy parity from day one. The habit of writing a Dockerfile before deploy means the app never runs locally in a way that doesn't translate to production. Docker Compose is the right tool for a two-service local stack; it's also a clear signal to technical reviewers that containerization is part of the engineering practice, not an afterthought.

---

### DECISION — Hosting: Render (backend) + Vercel (frontend) + GitHub Pages (HTML demo)

**Decision:** Three separate hosting targets for the three delivery surfaces.

**Reason:** Render has native Docker support and a persistent disk for SQLite — the only viable free-tier option for a containerized FastAPI + SQLite app. Vercel is the simplest Vite deploy path with zero config. GitHub Pages serves the HTML demo from the `demo/` folder directly — no build step, immediate availability. The three platforms are the best fit for each track's constraints; using one platform for all three would require compromises.

---

### DECISION — Model selection decoupled from service code via TaskComplexity tiers

**Decision:** Services declare a complexity tier (`REASONING` or `FAST`) rather than a model name. `core/config.py` resolves the tier to a model string at runtime via `resolve_model()`. Model strings are env-configurable; defaults are Claude Sonnet and Haiku.

**Reason:** Hardcoding model strings in service files couples the system to a specific provider and version. The tier pattern makes the intent of each AI call explicit ("this needs reasoning-level work") without locking in a vendor. Swapping models or providers requires changing two env vars — no service code changes. The resolved model name is still returned in every response so the UI always shows what actually ran.

---

### DECISION — Pre-build review: trim bloat before first line of code

**Decision:** Five cuts made to CLAUDE.md and PLAN.md during planning review before build started.

1. Removed `briefings` cache table — fresh generation per request is sufficient at demo scale; caching adds a table and cache-invalidation logic for no demo gain.
2. Removed `GET /api/brief/audit` endpoint and audit panel — the audit trail is already in the `actions` table (`approved_by`, `executed_at`); a dedicated endpoint + UI panel duplicates what the action status list already shows.
3. Removed `feasible` field from `decision_options` — only feasible options are seeded; this flag is never toggled in the demo.
4. Removed `pending_actions: int` from `BriefingResponse` — requires an extra DB query and adds nothing the action panel doesn't already surface.
5. Removed frontend service from `docker-compose.yml` — Docker Compose is backend only; building a production nginx container for a Vite app adds nginx config complexity with zero benefit. Frontend deploys to Vercel directly.

**Reason:** Cutting before building is cheaper than cutting after. None of these items appear in the core demo flow (see → decide → act → record) and each would cost real build time.

---

### DECISION — Track A: one HTML file with SIM_* constants

**Decision:** The HTML demo (`demo/index.html`) uses pre-written `SIM_*` JS objects for all AI responses. AI call functions are written but commented out.

**Reason:** Recruiters and LinkedIn viewers should not need an API key or a running server to see the system work. `SIM_*` outputs must match the exact schema of real AI responses so the demo is an honest representation, not a mockup. The commented stubs make the real implementation path transparent — a technical reviewer can see exactly what the AI call would look like.

---

## Build Log

### LESSON — `init_db.py` must run as a module, not a script
**From:** Phase 1
**Lesson:** `db/init_db.py` does `from core.config import DB_PATH`, a sibling-package import. Running it directly (`python db/init_db.py`) puts `db/` on `sys.path`, not `backend/`, so the import fails with `ModuleNotFoundError: No module named 'core'`. Running it as `uv run python -m db.init_db` from `backend/` puts the backend root on `sys.path` instead, which resolves correctly.
**Applied in:** PLAN.md and README.md run instructions updated to use the `-m db.init_db` form.

*Further PROBLEM, LESSON, and DECISION entries will be added here as the build continues.*

### Format for build entries:

```
### PROBLEM — [short description]
**Encountered:** Phase X, [date]
**What happened:** ...
**How it was resolved:** ...

### LESSON — [short description]
**From:** Phase X
**Lesson:** ...
**Applied in:** ...

### DECISION — [short description]
**Decision:** ...
**Reason:** ...
```

---

## Deploy Log

*Populated in Phase 6.*

| Surface | Platform | URL | Date |
|---|---|---|---|
| Track A (HTML demo) | GitHub Pages | — | — |
| Track B backend | Render | — | — |
| Track B frontend | Vercel | — | — |
