# PLAN.md — Palantir Foundry Operational Decision Platform

## Problem Statement

Enterprise organizations have fragmented operational data but no shared picture of current state, object dependencies, or available response actions. Decisions are made in isolation from the systems they affect. There is no governed loop from anomaly detection → decision support → authorized action → outcome recording.

**Who this solves it for:** Operations managers, planners, maintenance leads, and logistics coordinators who must act on incomplete information across disconnected systems.

**What the demo shows:** A working operational decision platform modeled on Palantir Foundry's architecture — with a live Ontology graph, AI-powered impact analysis, scenario comparison, and a governed action copilot. The entire loop: see → decide → act → record.

---

## Two-Track Scope

### Track A — HTML Demo

**In scope:**
- Single `demo/index.html` — three tabs, one file
- All three modules (OpsGraph, DecisionRoom, MissionBrief) in tabbed layout
- Inline mock data as JS objects
- `SIM_*` constants for all AI responses
- AI function stubs commented out (callable with real key)
- Hosted on GitHub Pages

**Out of scope (Track A):**
- Real API calls, backend, database
- Authentication or role-based access control
- Persistent state between sessions

### Track B — Real System

**In scope:**
- FastAPI backend — three router modules
- SQLite database with seed data
- React/Vite frontend with D3 dependency graph
- Real Anthropic API calls (Sonnet + Haiku)
- Docker Compose for local orchestration
- Deploy: Render (backend) + Vercel (frontend)

**Out of scope (Track B):**
- Production auth / SSO
- Multi-tenant data isolation
- Streaming AI responses (v2 feature)
- Write-back to external systems (mocked only)

---

## Architecture Decision Rationale

| Decision | Choice | Reason |
|---|---|---|
| Backend framework | FastAPI | Native async, Pydantic v2 integration, clean router pattern — fits AI service calls well |
| Database | SQLite | Three modules share one lightweight DB; no infra overhead for portfolio build |
| Frontend framework | React/Vite | Component model maps cleanly to three module panels; Vite is fast to scaffold |
| Graph rendering | D3.js | Force-directed graph is the right visualization for the Ontology dependency view; no abstraction needed |
| AI provider | Anthropic (Claude) | Sonnet for complex reasoning, Haiku for summarization — intentional model split |
| Containerization | Docker Compose | Backend containerized for local dev and Render deploy parity; frontend deploys to Vercel directly |
| Hosting (backend) | Render | Free tier, Docker-native, persistent disk for SQLite |
| Hosting (frontend) | Vercel | Zero-config Vite deploy, CDN, free tier |
| Module architecture | One repo, three modules | OpsGraph creates the data layer DecisionRoom and MissionBrief consume — shared foundation avoids duplication |

---

## Library Resources

> Skills from `~/Documents/GitHub/JaymsH14/claude_resource_staging/claude-skills` — reviewed via `project-planner` skill.

### Tier 1 Skills (auto-load — relevant to this build)
- `project-planner` — drives this plan-review/update cycle; re-run on demand with "update the plan"
- `claude-api` — Anthropic SDK usage for `services/ai_*.py` (model calls, tiering, error handling)
- `agentic-architecture-patterns` — informs the tier-based model routing and two-path error handling already in this plan
- `agent-memory-and-context` — relevant if briefing/decision history needs persistent context beyond SQLite later
- `frontend-design` — React component build quality for `OpsGraphView`, `DecisionRoomView`, `MissionBriefView`
- `git-worktree-devtools` — useful if phases are split across parallel work (Phase 2/3 can run in parallel per dependency notes)

### Tier 2/3 Skills (load when needed)
- none of the plugin-dev, MCP, or studio/digitalstone tiers apply — this is a standalone FastAPI/React build, not a plugin or MCP server

### Starters / Cookbooks
- No matching starter in `STARTER-INDEX.md` (closest is `financial-data-analyst` — Next.js, not the chosen stack) or `COOKBOOK-INDEX.md` — this build is custom, not scaffolded. No action needed.

---

## AI Strategy

### Task Complexity Tiers

Model selection is decoupled from service code. Services declare a complexity tier (`REASONING` or `FAST`); `core/config.py` resolves the tier to the configured model at runtime. Defaults are Claude — overridable via env vars without touching service code.

| Tier | Default model | Env var |
|---|---|---|
| `REASONING` | `claude-sonnet-4-6` | `AI_MODEL_REASONING` |
| `FAST` | `claude-haiku-4-5-20251001` | `AI_MODEL_FAST` |

### Task → Tier Assignments

| Module | Task | Tier | Reason |
|---|---|---|---|
| OpsGraph | Impact analysis — trace affected objects, explain dependency path | `REASONING` | Multi-object graph reasoning; explanation quality matters |
| DecisionRoom | Scenario recommendation — evaluate options against constraints | `REASONING` | Constraint evaluation + tradeoff synthesis |
| MissionBrief | Role briefing generation — summarize current operational state | `FAST` | Structured data → natural language; lighter task |
| MissionBrief | Action rationale — explain why a proposed action is appropriate | `FAST` | Narrow classification + one-paragraph explanation |

### What Stays Consistent
- All AI calls server-side — keys in env vars, never client
- Every AI panel shows a `ModelTag` with the resolved model name (what actually ran)
- Prompts are structured: system prompt (role + schema) + user prompt (data)
- AI reasoning always visible: scores, factors, confidence — never hidden
- `degraded_mode` and `ai_model` returned on every AI response

---

## System Architecture Flow

```
[User: Operations Manager / Planner / Maintenance Lead]
          |
          v
[Frontend: Dashboard.jsx — three tabs]
          |
    ┌─────┼─────────────────┐
    │     │                 │
    v     v                 v
[OpsGraph] [DecisionRoom] [MissionBrief]
    │     │                 │
    └─────┴─────────────────┘
                  |
          [API: client.js]
                  |
          [FastAPI Backend]
          ┌───────┼───────┐
          │       │       │
    [opsgraph] [decision] [brief]
    [router]   [router]   [router]
          │       │       │
    ┌─────┼───────┼───────┼──────┐
    │     │       │       │      │
    v     v       v       v      v
  [DB]  [AI    [AI     [AI    [DB
        Sonnet] Sonnet] Haiku] write]
          │       │       │
          └───────┴───────┘
                  |
        [ImpactResponse / RecommendationResponse / BriefingResponse]
                  |
          [Frontend renders result]
          - ModelTag (purple)
          - Confidence score
          - Reasoning breakdown
          - Exception badge (severity color)
```

---

## Phased Build Plan

### Phase 0 — Setup (30 min)

**Deliverable:** GitHub repo initialized, planning files committed, folder structure scaffolded.

Tasks:
- [ ] Create GitHub repo: `palantir-foundry-decision-platform`
- [ ] Commit planning files (CLAUDE.md, PLAN.md, README.md, build_journey.md, .gitignore)
- [ ] Scaffold full folder structure per CLAUDE.md
- [ ] Create `backend/.env.example` and `frontend/.env.example`
- [ ] `uv init` in `backend/` — generates `pyproject.toml`; `uv add fastapi "uvicorn[standard]" anthropic pydantic python-dotenv aiosqlite`
- [ ] Create `frontend/package.json` with exact dependencies
- [ ] Run `uv sync` (backend) and `npm install` (frontend) — confirm clean installs
- [ ] Initialize SQLite DB with `uv run db/init_db.py` — confirm tables created

*Dependency: none — start here*

---

### Phase 1 — Data Foundation (1.5 hr)

**Deliverable:** Database seeded with realistic mock data. All objects, links, events, options visible via GET routes.

Tasks:
- [ ] Write `db/init_db.py` — full DDL execution
- [ ] Write seed data: 6 objects (2 facilities, 2 assets, 1 order, 1 incident), 8 links, 3 events, 4 decision options
- [ ] Implement `routers/opsgraph.py` — GET `/objects`, GET `/objects/{id}`, GET `/links`, GET `/events`
- [ ] Implement `routers/decisionroom.py` — GET `/options/{event_id}`
- [ ] Test all GET routes with `curl` or HTTPie — confirm seed data returns correctly
- [ ] Write `core/errors.py` — `AIServiceError`, `LowConfidenceError`, `OntologyNotFoundError`

*Dependency: Phase 0 complete*

---

### Phase 2 — OpsGraph AI (2 hr)

**Deliverable:** Impact analysis endpoint working. D3 dependency graph renders in frontend. AI impact summary displayed with model tag.

Tasks:
- [ ] Implement `services/ai_opsgraph.py` — `analyze_impact()` with Sonnet
- [ ] System prompt: "You are an operational awareness assistant. Given a set of ontology objects and relationship links, identify all objects affected by a disruption to the specified object. Explain the dependency path."
- [ ] Implement `POST /api/opsgraph/impact` route
- [ ] Add two-path error handling: retry → degraded mode fallback
- [ ] Build `OpsGraphView.jsx` layout — object list panel + graph canvas + impact panel
- [ ] Build `DependencyGraph.jsx` — D3 force-directed graph from link data
- [ ] Build `ObjectPanel.jsx` — click object to select, show status badge
- [ ] Build `ImpactSummary.jsx` — calls POST /impact on selection, renders summary + model tag
- [ ] Add `ConfidenceFlag.jsx` — renders when `confidence < 0.7`
- [ ] Test: select a degraded object → impact analysis returns → graph highlights affected nodes

*Dependency: Phase 1 complete*

---

### Phase 3 — DecisionRoom AI (2 hr)

**Deliverable:** Scenario comparison and recommendation endpoint working. Constraint editor lets user adjust weights. Recommendation card shows rationale and confidence.

Tasks:
- [ ] Implement `services/ai_decision.py` — `recommend_option()` with Sonnet
- [ ] System prompt: "You are an operational decision advisor. Given a list of response options and user-defined constraints with weights, evaluate each option and recommend the best choice. Explain your reasoning and identify which constraint tradeoffs most affect the decision."
- [ ] Implement `POST /api/decision/recommend` route
- [ ] Implement `POST /api/decision/record` route — saves decision to DB
- [ ] Add two-path error handling consistent with Phase 2 pattern
- [ ] Build `DecisionRoomView.jsx` — event selector + option list + constraint panel + recommendation panel
- [ ] Build `ScenarioPanel.jsx` — lists options for selected event, show cost/service/risk scores
- [ ] Build `ConstraintEditor.jsx` — sliders for constraint weights (cost, service, risk)
- [ ] Build `RecommendationCard.jsx` — shows recommended option, rationale, confidence, constraint scores
- [ ] Test: select event → adjust constraints → request recommendation → approve → record saved

*Dependency: Phase 1 complete (OpsGraph can run in parallel)*

---

### Phase 4 — MissionBrief AI (1.5 hr)

**Deliverable:** Role briefing generation working. Action proposal and approval flow complete. Audit log visible.

Tasks:
- [ ] Implement `services/ai_brief.py` — `generate_briefing()` and `generate_action_rationale()` with Haiku
- [ ] Implement `POST /api/brief/generate` route
- [ ] Implement `POST /api/brief/action` and `POST /api/brief/action/{id}/approve` routes
- [ ] Implement `GET /api/brief/actions` route — returns actions list with status
- [ ] Build `MissionBriefView.jsx` — role selector + briefing panel + action queue
- [ ] Build `RoleSelector.jsx` — four role options, triggers briefing generation on select
- [ ] Build `BriefingPanel.jsx` — renders markdown briefing, model tag, top exceptions list
- [ ] Build `ActionApproval.jsx` — pending actions list, approve/reject buttons, status badges
- [ ] Test: select role → briefing generated → propose action → approve → action status updates

*Dependency: Phases 1 + 2 complete (shares object and event data)*

---

### Phase 5 — Track A HTML Demo (1.5 hr)

**Deliverable:** `demo/index.html` — single file, three tabs, all three modules working with SIM data.

Tasks:
- [ ] Create `demo/index.html` structure — tab nav, module panels, design tokens inline
- [ ] Write `SIM_IMPACT` object — pre-written impact analysis result
- [ ] Write `SIM_RECOMMENDATION` object — pre-written recommendation with constraint scores
- [ ] Write `SIM_BRIEFING` object — pre-written briefing for operations_manager role
- [ ] Stub AI call functions — commented out, with note showing how to enable with real key
- [ ] Implement OpsGraph tab — object list, static D3 graph from inline data, impact panel using SIM_IMPACT
- [ ] Implement DecisionRoom tab — options list, constraint sliders (cosmetic), recommendation from SIM_RECOMMENDATION
- [ ] Implement MissionBrief tab — role selector, briefing from SIM_BRIEFING, action buttons (cosmetic)
- [ ] Test: open in browser with no server — all three tabs render, no console errors

*Dependency: Phases 2–4 complete (so SIM outputs match real output schemas)*

---

### Phase 6 — Containerization + Deploy + Review (1.5 hr)

**Deliverable:** Docker Compose working locally. Backend on Render, frontend on Vercel, HTML demo on GitHub Pages. 60-second viewer test passed.

Tasks:
- [ ] Write `backend/Dockerfile` per CLAUDE.md spec
- [ ] Write `docker-compose.yml` per CLAUDE.md spec (backend only)
- [ ] Test `docker-compose up` — backend API accessible at localhost:8000, confirm `/docs` reachable
- [ ] Deploy backend to Render — connect GitHub repo, set env vars, confirm `/docs` reachable
- [ ] Deploy frontend to Vercel — set `VITE_API_BASE_URL` to Render URL, confirm app loads
- [ ] Enable GitHub Pages on `demo/` folder — confirm `index.html` reachable at pages URL
- [ ] Update README.md with live URLs (Track A and Track B)
- [ ] Log deploy URLs in `build_journey.md`
- [ ] Confirm all model tags visible in Track B UI
- [ ] Confirm degraded mode triggers on simulated AI failure
- [ ] Update `build_journey.md` with LESSON entries from the build
- [ ] Final commit with tag `v1.0`

*Dependency: Phases 2–5 complete*

---

## Containerization Plan

`backend/Dockerfile` builds a slim Python 3.12 image, installs requirements, exposes port 8000.

`docker-compose.yml` runs the backend only. The SQLite DB is mounted as a volume at `/app/db/` so data persists across container restarts in local dev. Frontend deploys to Vercel directly — no nginx container needed.

For Render deployment: Docker build from `./backend`, env vars set in Render dashboard. SQLite persists on Render's persistent disk.

---

## Deployment Configuration

### Render (backend)
- Build command: Docker (point to `backend/Dockerfile`)
- Start command: handled by Dockerfile CMD
- Env vars: `ANTHROPIC_API_KEY`, `DATABASE_URL`, `FRONTEND_URL`
- Persistent disk: mounted at `/app/db/`

### Vercel (frontend)
- Framework: Vite
- Build command: `npm run build`
- Output dir: `dist`
- Env var: `VITE_API_BASE_URL=https://[render-service].onrender.com`

### GitHub Pages (HTML demo)
- Source: `demo/` folder on `main` branch
- No build step — raw HTML file served directly

---

## Portfolio Framing Language

> "I built a three-module operational decision platform modeled on Palantir Foundry's architecture. Each module adds a layer: OpsGraph makes the Ontology visible, DecisionRoom makes the decision comparable, and MissionBrief closes the loop with governed actions. The AI reasoning is always visible — scores, confidence, constraint tradeoffs — not hidden. Built in two tracks: zero-setup HTML demo for recruiters, production FastAPI + React system for the portfolio."

---

## Claude Code Handoff

### What's done (from planning session):
- CLAUDE.md: complete — schema, models, routes, component tree, AI services, tokens, conventions
- PLAN.md: complete — all phases, tasks, architecture decisions
- README.md: complete — portfolio landing page with live link placeholders
- build_journey.md: initialized with all planning decisions
- .gitignore: complete

### First three actions for Claude Code:
1. `cd palantir-foundry-decision-platform/backend && uv sync && cd ../frontend && npm install` — confirm clean installs
2. `uv run --directory backend db/init_db.py` — create tables and seed data, confirm all objects/links/events return from GET routes
3. Start Phase 2: implement `services/ai_opsgraph.py` and `POST /api/opsgraph/impact` — this is the first AI call in the system

### Open questions before deploy:
- Render persistent disk size — default 1GB is sufficient for SQLite at this scale
- GitHub Pages: confirm `demo/` folder deploy works or if root deploy + redirect needed
- D3 version compatibility with React 18 strict mode — test in Phase 2 before committing to the pattern

---

## Current Status
**Active phase:** Phase 0 — Setup (not yet started)
**Last updated:** 2026-06-19
**Notes:** Plan reviewed via `project-planner` skill. Architecture, phasing, and AI strategy confirmed sound — no structural changes needed. Sole correction: Python dependency management switched from `pip`/`requirements.txt` to `uv` throughout (Phase 0, Claude Code Handoff) to match mandatory dev standard. `CLAUDE.md` and `README.md` updated to match.
