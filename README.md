# Palantir Foundry Operational Decision Platform

**An AI-powered operational decision system modeled on Palantir Foundry's architecture.**  
Three modules. One governed loop: see the operation → compare decisions → execute authorized actions.

---

**Track A Demo:** Standalone — download `demo/index.html` and open it directly in your browser, or preview it from this repo. No server, no build step, no account needed.
**Track B (Real System):** Not deployed by default. See [Deploying Track B](#deploying-track-b-render--vercel) below — it's a few clicks against your own Render/Vercel accounts.

---

## The Problem

Enterprise organizations rarely lack data. They lack a shared operational picture.

Orders live in one system. Assets in another. Schedules, commitments, incidents, and teams are scattered. A dashboard can aggregate some of this — but it still leaves the operator asking: what is affected? Why does it matter? What can I do? Who is allowed to act?

This project models the Palantir Foundry design pattern: build a governed data foundation, map it into an operational Ontology, add AI reasoning at the decision points, and close the loop with authorized actions.

---

## System Architecture

```
[Operational Data Sources]
  facilities · assets · orders · incidents · teams
          |
          v
[Ontology Layer — objects + links + events]
          |
     ┌────┼────────────────┐
     │    │                │
     v    v                v
[OpsGraph AI]   [DecisionRoom AI]   [MissionBrief AI]
  See the          Compare the         Brief the role,
  operation        options             execute actions
     │    │                │
     └────┴────────────────┘
          |
[Decision Record + Audit Trail]
```

---

## Modules

### OpsGraph AI

Makes the Ontology visible. Loads operational objects — facilities, assets, orders, incidents, teams — and renders their dependency relationships as an interactive graph. Select any object to trace upstream and downstream dependencies. Request an AI impact analysis when an exception occurs.

**AI:** The `REASONING`-tier model traces the dependency path and explains which objects are affected by a disruption and why. The reasoning is shown in full — not summarized into a single score.

### DecisionRoom AI

Turns a disruption into a structured decision. For a selected event, the system loads response options and lets the operator adjust constraint weights — cost, service level, capacity risk. The `REASONING`-tier model evaluates each option against the weighted constraints and produces a ranked recommendation with full tradeoff explanation.

**AI:** Constraint evaluation and multi-option tradeoff synthesis. The recommendation shows which constraint drove the decision and what would change the answer.

### MissionBrief AI

A role-aware operational briefing and action copilot. Select a role — operations manager, planner, maintenance lead, logistics lead — and the system generates a focused brief of current state, top exceptions, and pending decisions. Propose a governed action; it requires approval before execution. Every action is logged to the audit trail.

**AI:** The `FAST`-tier model generates the role briefing and explains proposed actions. The full prompt-to-response cycle is intentionally visible in the UI — model tag, confidence, rationale shown.

---

## AI Strategy

Model selection is decoupled from service code. Each task declares a complexity tier; the system resolves it to a configured model at runtime. Defaults are Claude — swap model or provider by changing two env vars, no service code changes.

| Tier | Default model | Env var |
|---|---|---|
| `REASONING` | `claude-sonnet-4-6` | `AI_MODEL_REASONING` |
| `FAST` | `claude-haiku-4-5-20251001` | `AI_MODEL_FAST` |

| Module | Task | Tier | Reason |
|---|---|---|---|
| OpsGraph | Impact analysis — trace affected objects across the graph | `REASONING` | Multi-object dependency reasoning; explanation quality matters |
| DecisionRoom | Scenario recommendation — evaluate options vs. constraints | `REASONING` | Constraint evaluation + tradeoff synthesis |
| MissionBrief | Role briefing — summarize current operational state | `FAST` | Structured data → natural language; lighter task |
| MissionBrief | Action rationale — explain a proposed action | `FAST` | Narrow classification + one-paragraph explanation |

Every AI panel shows the resolved model name (what actually ran). AI reasoning is always visible — scores, factors, confidence — never hidden.

---

## Error Handling

**Path 1 — Automated recovery:**  
AI failure → retry once → fall back to logic-only result with `⚠ degraded` badge. Confidence below threshold → re-score with lower threshold → show result with `⚠ low confidence` flag.

**Path 2 — Human routing:**  
When recovery fails, the exception is logged to the queue with full context. A human acts; the override is recorded. One queue: business anomalies and system failures both surface here.

---

## Tech Stack

### Track A — HTML Demo

| Layer | Choice |
|---|---|
| Delivery | Single `index.html` |
| Data | Inline JS objects |
| AI | `SIM_*` constants (stubs callable with real key) |
| Graph | D3.js v7 (CDN) |
| Hosting | GitHub Pages |

### Track B — Real System

| Layer | Choice |
|---|---|
| Backend | Python / FastAPI |
| Database | SQLite (aiosqlite) |
| AI | Anthropic SDK (model-tier configurable via env vars) |
| Frontend | React 18 / Vite |
| Graph | D3.js v7 |
| Containerization | Docker + Docker Compose |
| Backend hosting | Render |
| Frontend hosting | Vercel |

---

## Project Folder Structure

```
palantir-foundry-decision-platform/
├── demo/
│   └── index.html              # Track A — all three modules, no backend
├── backend/
│   ├── main.py
│   ├── pyproject.toml
│   ├── Dockerfile
│   ├── db/
│   ├── models/
│   ├── routers/
│   ├── services/
│   └── core/
├── frontend/
│   ├── package.json
│   └── src/
│       ├── api/
│       ├── styles/
│       ├── components/
│       └── pages/
└── docker-compose.yml
```

---

## Run Locally

### HTML Demo (Track A) — standalone, no setup

`demo/index.html` is a single self-contained file. There is nothing to install and nothing to connect:

```bash
open demo/index.html
# or just double-click it in your file browser — no server needed
```

It uses pre-captured real AI responses (`SIM_*` constants, captured verbatim from live Sonnet/Haiku calls
during development — see `build_journey.md`) instead of calling the API live, since a static HTML file can't
safely hold a secret key. The real call functions are written in the file's `<script>` block, commented out,
so you can see exactly what the live version does.

### Full System (Track B)

**Backend:**
```bash
cd backend
uv sync
cp .env.example .env       # add your ANTHROPIC_API_KEY
uv run python -m db.init_db  # create tables + seed data
uv run uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
cp .env.example .env       # VITE_API_BASE_URL=http://localhost:8000
npm run dev
```

Open `http://localhost:5173`

---

## Docker

```bash
# from repo root
cp backend/.env.example backend/.env   # add your ANTHROPIC_API_KEY
docker-compose up --build
```

Backend: `http://localhost:8000`  
Frontend: `http://localhost:5173`  
API docs: `http://localhost:8000/docs`

---

## Deploying Track B (Render + Vercel)

Track B is not deployed by default — running it live requires your own Anthropic API key and your own
hosting accounts, so this is left for you to connect. Here's what each piece is for and exactly how to wire
it up.

### Render — backend hosting
**Purpose:** Runs the FastAPI backend (the part that holds your `ANTHROPIC_API_KEY` and talks to Claude) as
an always-on container with a persistent disk for the SQLite database. Render's free tier supports Docker
builds and persistent disk, which Vercel/Netlify-style static hosts don't.

**To connect:**
1. Create a Render account, then **New → Web Service**, connect this GitHub repo.
2. Set the root directory to `backend/`, and the build to use `backend/Dockerfile` (Render auto-detects it).
3. Add environment variables in the Render dashboard: `ANTHROPIC_API_KEY` (your real key), `DATABASE_URL=./db/foundry.db`,
   `FRONTEND_URL` (your eventual Vercel URL, can be updated after step below), `PORT=8000`, plus
   `AI_MODEL_REASONING` / `AI_MODEL_FAST` if you want to override the defaults.
4. Add a persistent disk mounted at `/app/db` so the SQLite database survives restarts/redeploys.
5. Deploy. Once live, confirm `https://<your-service>.onrender.com/docs` loads the FastAPI Swagger UI —
   that's the same proof-of-life check used throughout development.

### Vercel — frontend hosting
**Purpose:** Builds and serves the React/Vite frontend as a static site with zero server config.

**To connect:**
1. Create a Vercel account, **Add New → Project**, import this GitHub repo.
2. Set the root directory to `frontend/`. Vercel auto-detects the Vite framework preset
   (build command `npm run build`, output directory `dist`).
3. Add the environment variable `VITE_API_BASE_URL=https://<your-render-service>.onrender.com` (the URL from
   the Render step above).
4. Deploy. Once live, go back to your Render service's `FRONTEND_URL` env var and set it to your new Vercel
   URL, then redeploy the backend so CORS allows requests from it.

### GitHub Pages — optional hosted preview of the Track A demo
**Purpose:** The demo is meant to be downloaded and opened locally — that's the whole point of it being a
single offline file. GitHub Pages is only useful if you'd rather send people a link than a file.

**To connect:**
1. In this repo's GitHub Settings → Pages, set the source to the `main` branch, `/demo` folder.
2. Once enabled, `demo/index.html` is reachable directly at the Pages URL GitHub gives you — no build step.

---

## Environment Variables

```bash
# backend/.env
ANTHROPIC_API_KEY=
DATABASE_URL=./db/foundry.db
FRONTEND_URL=http://localhost:5173
PORT=8000

# frontend/.env
VITE_API_BASE_URL=http://localhost:8000
```

---

## Portfolio Context

This is entry **04** in a weekly AI systems build series. Each entry follows the same format:

**Problem → Architecture → Build → Deploy → Results**

The series demonstrates the ability to identify a real operational problem, design a system to solve it, build it lean, deploy it, and explain the engineering decisions. Every entry is disciplined and working — not a polished product, not a toy.

The full decision log is in [`build_journey.md`](./build_journey.md).

---

## What This Demonstrates

- Ontology-first operational AI design — the AI reasons about governed objects, not raw tables
- Multi-module system architecture — three modules sharing one data foundation
- Tier-based model routing — tasks declare complexity (`REASONING` / `FAST`), system resolves the model at runtime via env-configurable map
- Human-in-the-loop execution — approval flows, audit trails, exception routing
- Two-path error handling — automated recovery + human escalation
- Dual-track delivery — zero-setup HTML demo + production-grade full stack
- Containerization habit — Docker Compose planned and included from day one

---

## Builder

**Jayms** — AI systems engineer  
Weekly AI Systems Build Series · Entry 04 of ongoing
