# CLAUDE.md — Palantir Foundry Operational Decision Platform

## Project Overview

**Repo:** `palantir-foundry-decision-platform`  
**Series entry:** 04 — Palantir Foundry: Operational Decision Platform  
**Problem:** Enterprise organizations have fragmented operational data but no shared picture of current state, dependencies, or available response actions. Decisions happen in isolation from the systems they affect.  
**AI value:** AI makes the operational graph readable, anomalies visible, decisions comparable, and actions explainable — at the speed and complexity that humans alone cannot sustain.

### Dual-Track Architecture

**Track A — HTML Demo** (`demo/index.html`)  
Single file, no backend, no build step. Opens in any browser. All data inline as JS objects. AI call functions written but commented out. Falls back to `SIM_*` constants. Hosted on GitHub Pages.

**Track B — Real System** (`backend/` + `frontend/`)  
FastAPI backend + React/Vite frontend. Real AI calls server-side. Docker-ready. Hosted on Render (backend) + Vercel (frontend).

### Three Modules — One Repo, One Progression

The three demos share data, design tokens, and the Ontology layer. Each adds a capability layer on top:

| Module | What it does | Builds on |
|---|---|---|
| **OpsGraph AI** | Ontology viewer + dependency graph + impact analysis | — (foundation) |
| **DecisionRoom AI** | Scenario comparison + constraint evaluation + recommendation | OpsGraph data layer |
| **MissionBrief AI** | Role-aware briefing + governed action copilot | OpsGraph + DecisionRoom |

---

## Folder Structure

```
palantir-foundry-decision-platform/
├── CLAUDE.md
├── PLAN.md
├── README.md
├── build_journey.md
├── .gitignore
├── demo/
│   └── index.html                  # Track A — all three modules tabbed
├── backend/
│   ├── main.py                     # FastAPI app + router mounts
│   ├── pyproject.toml               # uv-managed dependencies
│   ├── uv.lock
│   ├── .env.example
│   ├── Dockerfile
│   ├── db/
│   │   ├── init_db.py              # DDL execution + seed data
│   │   └── foundry.db              # SQLite (gitignored)
│   ├── models/
│   │   ├── ontology.py             # Pydantic models — objects, links, events
│   │   ├── decision.py             # Pydantic models — options, constraints, outcomes
│   │   └── brief.py                # Pydantic models — briefing, actions
│   ├── routers/
│   │   ├── opsgraph.py             # /api/opsgraph/* routes
│   │   ├── decisionroom.py         # /api/decision/* routes
│   │   └── missionbrief.py         # /api/brief/* routes
│   ├── services/
│   │   ├── ai_opsgraph.py          # AI calls for OpsGraph module
│   │   ├── ai_decision.py          # AI calls for DecisionRoom module
│   │   └── ai_brief.py             # AI calls for MissionBrief module
│   └── core/
│       ├── config.py               # env var loading
│       └── errors.py               # exception types + handlers
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── .env.example
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── api/
│       │   └── client.js           # centralized fetch wrapper
│       ├── styles/
│       │   └── tokens.css          # design system CSS variables
│       ├── components/
│       │   ├── shared/
│       │   │   ├── ModelTag.jsx
│       │   │   ├── ExceptionBadge.jsx
│       │   │   └── ConfidenceFlag.jsx
│       │   ├── opsgraph/
│       │   │   ├── OpsGraphView.jsx
│       │   │   ├── DependencyGraph.jsx
│       │   │   ├── ObjectPanel.jsx
│       │   │   └── ImpactSummary.jsx
│       │   ├── decisionroom/
│       │   │   ├── DecisionRoomView.jsx
│       │   │   ├── ScenarioPanel.jsx
│       │   │   ├── ConstraintEditor.jsx
│       │   │   └── RecommendationCard.jsx
│       │   └── missionbrief/
│       │       ├── MissionBriefView.jsx
│       │       ├── RoleSelector.jsx
│       │       ├── BriefingPanel.jsx
│       │       └── ActionApproval.jsx
│       └── pages/
│           └── Dashboard.jsx       # top-level tab router
└── docker-compose.yml
```

---

## Database Schema (SQLite)

```sql
-- Ontology Objects (assets, orders, facilities, incidents, teams)
CREATE TABLE objects (
    id          TEXT PRIMARY KEY,
    type        TEXT NOT NULL,           -- 'facility' | 'asset' | 'order' | 'incident' | 'team'
    name        TEXT NOT NULL,
    status      TEXT NOT NULL,           -- 'nominal' | 'at_risk' | 'degraded' | 'critical'
    owner_id    TEXT,
    metadata    TEXT,                    -- JSON blob
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

-- Ontology Links (relationships between objects)
CREATE TABLE links (
    id          TEXT PRIMARY KEY,
    source_id   TEXT NOT NULL REFERENCES objects(id),
    target_id   TEXT NOT NULL REFERENCES objects(id),
    type        TEXT NOT NULL,           -- 'serves' | 'depends_on' | 'located_at' | 'assigned_to' | 'affects'
    weight      REAL DEFAULT 1.0,
    created_at  TEXT NOT NULL
);

-- Events (exceptions, anomalies, status changes)
CREATE TABLE events (
    id          TEXT PRIMARY KEY,
    object_id   TEXT NOT NULL REFERENCES objects(id),
    type        TEXT NOT NULL,           -- 'anomaly' | 'exception' | 'alert' | 'status_change'
    severity    TEXT NOT NULL,           -- 'urgent' | 'high' | 'normal'
    description TEXT NOT NULL,
    resolved    INTEGER DEFAULT 0,       -- 0 | 1
    created_at  TEXT NOT NULL
);

-- Decision Options (for DecisionRoom)
CREATE TABLE decision_options (
    id              TEXT PRIMARY KEY,
    event_id        TEXT NOT NULL REFERENCES events(id),
    label           TEXT NOT NULL,
    description     TEXT NOT NULL,
    cost_impact     REAL,
    service_impact  REAL,
    risk_score      REAL,
    created_at      TEXT NOT NULL
);

-- Decision Records (approved outcomes)
CREATE TABLE decision_records (
    id              TEXT PRIMARY KEY,
    event_id        TEXT NOT NULL REFERENCES events(id),
    option_id       TEXT REFERENCES decision_options(id),
    rationale       TEXT,
    decided_by      TEXT NOT NULL,
    decided_at      TEXT NOT NULL,
    outcome_notes   TEXT,
    ai_model        TEXT
);

-- Actions (for MissionBrief — governed write-back)
CREATE TABLE actions (
    id              TEXT PRIMARY KEY,
    type            TEXT NOT NULL,       -- 'reassign' | 'escalate' | 'schedule' | 'notify' | 'defer'
    object_id       TEXT NOT NULL REFERENCES objects(id),
    requested_by    TEXT NOT NULL,
    approved_by     TEXT,
    status          TEXT NOT NULL,       -- 'pending' | 'approved' | 'rejected' | 'executed'
    payload         TEXT,               -- JSON — action-specific parameters
    ai_rationale    TEXT,
    created_at      TEXT NOT NULL,
    executed_at     TEXT
);
```

---

## Data Models (Pydantic)

### `models/ontology.py`

```python
from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime

ObjectType = Literal["facility", "asset", "order", "incident", "team"]
StatusType = Literal["nominal", "at_risk", "degraded", "critical"]
LinkType = Literal["serves", "depends_on", "located_at", "assigned_to", "affects"]
SeverityType = Literal["urgent", "high", "normal"]

class OntologyObject(BaseModel):
    id: str
    type: ObjectType
    name: str
    status: StatusType
    owner_id: Optional[str] = None
    metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

class OntologyLink(BaseModel):
    id: str
    source_id: str
    target_id: str
    type: LinkType
    weight: float = 1.0
    created_at: datetime

class Event(BaseModel):
    id: str
    object_id: str
    type: Literal["anomaly", "exception", "alert", "status_change"]
    severity: SeverityType
    description: str
    resolved: bool = False
    created_at: datetime

class ImpactAnalysisRequest(BaseModel):
    object_id: str
    event_id: Optional[str] = None

class ImpactAnalysisResponse(BaseModel):
    object_id: str
    affected_objects: list[str]
    dependency_path: list[dict]
    summary: str
    confidence: float
    ai_model: str
    degraded_mode: bool = False
```

### `models/decision.py`

```python
from pydantic import BaseModel
from typing import Optional

class DecisionOption(BaseModel):
    id: str
    event_id: str
    label: str
    description: str
    cost_impact: Optional[float] = None
    service_impact: Optional[float] = None
    risk_score: Optional[float] = None

class Constraint(BaseModel):
    name: str
    threshold: float
    weight: float                   # 0.0–1.0 importance weighting

class ScenarioRequest(BaseModel):
    event_id: str
    constraints: list[Constraint]

class RecommendationResponse(BaseModel):
    recommended_option_id: str
    rationale: str
    confidence: float
    tradeoff_summary: str
    constraint_scores: dict[str, float]
    ai_model: str
    degraded_mode: bool = False

class DecisionRecordCreate(BaseModel):
    event_id: str
    option_id: str
    rationale: str
    decided_by: str
```

### `models/brief.py`

```python
from pydantic import BaseModel
from typing import Optional, Literal

RoleType = Literal["operations_manager", "planner", "maintenance_lead", "logistics_lead"]
ActionType = Literal["reassign", "escalate", "schedule", "notify", "defer"]
ActionStatus = Literal["pending", "approved", "rejected", "executed"]

class BriefingRequest(BaseModel):
    role: RoleType

class BriefingResponse(BaseModel):
    role: RoleType
    content: str
    top_exceptions: list[str]
    generated_at: str
    ai_model: str

class ActionRequest(BaseModel):
    type: ActionType
    object_id: str
    requested_by: str
    payload: Optional[dict] = None

class ActionApproval(BaseModel):
    action_id: str
    approved_by: str
    approved: bool

class ActionResponse(BaseModel):
    action_id: str
    status: ActionStatus
    ai_rationale: str
    ai_model: str
```

---

## API Routes

### OpsGraph — `/api/opsgraph`

| Method | Path | Request | Returns |
|---|---|---|---|
| GET | `/objects` | — | `list[OntologyObject]` |
| GET | `/objects/{id}` | — | `OntologyObject` |
| GET | `/links` | `?source_id=&target_id=` | `list[OntologyLink]` |
| GET | `/events` | `?severity=&resolved=` | `list[Event]` |
| POST | `/impact` | `ImpactAnalysisRequest` | `ImpactAnalysisResponse` |

### DecisionRoom — `/api/decision`

| Method | Path | Request | Returns |
|---|---|---|---|
| GET | `/options/{event_id}` | — | `list[DecisionOption]` |
| POST | `/recommend` | `ScenarioRequest` | `RecommendationResponse` |
| POST | `/record` | `DecisionRecordCreate` | `DecisionRecord` |
| GET | `/records` | `?event_id=` | `list[DecisionRecord]` |

### MissionBrief — `/api/brief`

| Method | Path | Request | Returns |
|---|---|---|---|
| POST | `/generate` | `BriefingRequest` | `BriefingResponse` |
| POST | `/action` | `ActionRequest` | `ActionResponse` |
| POST | `/action/{id}/approve` | `ActionApproval` | `ActionResponse` |
| GET | `/actions` | `?status=&object_id=` | `list[ActionResponse]` |

---

## Frontend Component Tree

```
Dashboard.jsx
├── [tab: OpsGraph]  → OpsGraphView.jsx
│   ├── ObjectPanel.jsx           → GET /api/opsgraph/objects
│   ├── DependencyGraph.jsx       → GET /api/opsgraph/links
│   └── ImpactSummary.jsx         → POST /api/opsgraph/impact
│       └── ModelTag.jsx
│
├── [tab: DecisionRoom] → DecisionRoomView.jsx
│   ├── ScenarioPanel.jsx         → GET /api/decision/options/{event_id}
│   ├── ConstraintEditor.jsx      → (local state)
│   └── RecommendationCard.jsx    → POST /api/decision/recommend
│       ├── ModelTag.jsx
│       └── ConfidenceFlag.jsx
│
└── [tab: MissionBrief] → MissionBriefView.jsx
    ├── RoleSelector.jsx          → (local state)
    ├── BriefingPanel.jsx         → POST /api/brief/generate
    │   └── ModelTag.jsx
    └── ActionApproval.jsx        → POST /api/brief/action + GET /api/brief/actions
        └── ExceptionBadge.jsx
```

All API calls go through `src/api/client.js`:
```js
const BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
export async function apiFetch(path, options = {}) { ... }
```

---

## AI Service Pattern

### Task Complexity Tiers

Services never reference a model name directly. They declare a complexity tier; `core/config.py` resolves it to the configured model at runtime.

```python
# core/config.py
from enum import Enum
import os

class TaskComplexity(str, Enum):
    REASONING = "reasoning"   # multi-step, explanation-heavy tasks
    FAST      = "fast"        # summarization, template-style output

MODEL_MAP: dict[TaskComplexity, str] = {
    TaskComplexity.REASONING: os.getenv("AI_MODEL_REASONING", "claude-sonnet-4-6"),
    TaskComplexity.FAST:      os.getenv("AI_MODEL_FAST",      "claude-haiku-4-5-20251001"),
}

def resolve_model(complexity: TaskComplexity) -> str:
    return MODEL_MAP[complexity]
```

### Task → Tier Assignments

| Task | Tier | Default model | Reason |
|---|---|---|---|
| Impact analysis (OpsGraph) | `REASONING` | `claude-sonnet-4-6` | Multi-object dependency reasoning + explanation |
| Scenario recommendation (DecisionRoom) | `REASONING` | `claude-sonnet-4-6` | Constraint evaluation + tradeoff synthesis |
| Role briefing generation (MissionBrief) | `FAST` | `claude-haiku-4-5-20251001` | Structured data → natural language summary |
| Action rationale (MissionBrief) | `FAST` | `claude-haiku-4-5-20251001` | Narrow classification + one-paragraph explanation |

To swap models: set `AI_MODEL_REASONING` or `AI_MODEL_FAST` in `.env`. No service code changes.

### Function Signatures

```python
# services/ai_opsgraph.py
from core.config import TaskComplexity, resolve_model

async def analyze_impact(
    object_id: str,
    objects: list[dict],
    links: list[dict],
    event: dict | None
) -> ImpactAnalysisResponse:
    model = resolve_model(TaskComplexity.REASONING)
    # ... call model, return response with ai_model=model

# services/ai_decision.py
async def recommend_option(
    event: dict,
    options: list[dict],
    constraints: list[Constraint]
) -> RecommendationResponse:
    model = resolve_model(TaskComplexity.REASONING)
    ...

# services/ai_brief.py
async def generate_briefing(
    role: str,
    objects: list[dict],
    events: list[dict]
) -> BriefingResponse:
    model = resolve_model(TaskComplexity.FAST)
    ...

async def generate_action_rationale(
    action_type: str,
    object_data: dict
) -> str:
    model = resolve_model(TaskComplexity.FAST)
    ...
```

The resolved model string is always returned in the response (`ai_model` field) so the UI model tag reflects what actually ran.

### Prompt Strategy

Every AI call uses a two-part structure:
- **System prompt:** defines the role, operational context, and output schema
- **User prompt:** contains the actual data — objects, links, events, constraints

No open-ended prompts. Every prompt specifies exact output fields expected.

---

## Environment Variables

```bash
# backend/.env
ANTHROPIC_API_KEY=
DATABASE_URL=./db/foundry.db
FRONTEND_URL=http://localhost:5173
PORT=8000

# Model tier overrides — defaults to Claude if not set
AI_MODEL_REASONING=claude-sonnet-4-6
AI_MODEL_FAST=claude-haiku-4-5-20251001

# frontend/.env
VITE_API_BASE_URL=http://localhost:8000
```

---

## Dependencies

### Backend (`pyproject.toml`, managed via `uv`)
```
fastapi
uvicorn[standard]
anthropic
pydantic
python-dotenv
aiosqlite
```
Installed with `uv add <package>`, never `pip install`. Run scripts with `uv run`, never bare `python`/`python3`.

### Frontend (`package.json` dependencies)
```json
{
  "react": "^18",
  "react-dom": "^18",
  "vite": "^5",
  "@vitejs/plugin-react": "^4",
  "d3": "^7"
}
```
D3 is used for the dependency graph visualization in OpsGraph. No other UI library needed.

---

## Design System Tokens

```css
/* src/styles/tokens.css — identical tokens used in Track A index.html */
:root {
  --bg:           #0d1117;
  --surface:      #161b22;
  --surface-2:    #1c2128;
  --surface-3:    #21262d;
  --border:       #30363d;
  --blue:         #58a6ff;
  --purple:       #bc8cff;   /* Claude model color */
  --orange:       #e3b341;
  --red:          #f85149;
  --text:         #e6edf3;
  --text-muted:   #8b949e;
  --text-subtle:  #484f58;
}
```

Visual rules:
- Dark theme throughout — looks like a real ops console
- Purple `ModelTag` on every AI panel that uses Claude
- Severity color: urgent = red, high = orange, normal = blue
- AI reasoning always visible: scores, confidence, constraint breakdowns — never hidden
- Degraded mode: orange warning indicator on panel header
- Low-confidence result: shown with flag, never hidden

---

## Coding Conventions

### Python (backend)
- FastAPI with `APIRouter` per module — never mix routing into `main.py`
- Pydantic v2 models for all request/response shapes
- `async/await` throughout — aiosqlite for DB, httpx or anthropic SDK for AI
- Business logic in `services/` — routers call services, never DB directly
- Environment config via `core/config.py` using `python-dotenv`
- No inline SQL in routers — all queries in `db/` helpers

### TypeScript / JavaScript (frontend)
- Functional components + hooks only
- All API calls through `src/api/client.js` — no direct `fetch()` elsewhere
- Local state (`useState`) before any global state management
- D3 graph renders in a `useEffect` with a `ref` — not managed by React diffing
- Component files named `PascalCase.jsx`

---

## Containerization

### `backend/Dockerfile`
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY pyproject.toml uv.lock .
RUN uv sync --frozen --no-dev
COPY . .
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### `docker-compose.yml` (root)

Backend only. Frontend deploys to Vercel directly — no nginx container needed.

```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    volumes:
      - ./backend/db:/app/db
```

---

## Error Handling Design

### Path 1 — Automated Recovery

1. AI API call fails → retry once with 2-second backoff
2. Retry fails → fall back to logic-only result, set `degraded_mode: true` in response
3. No result above confidence threshold (< 0.5) → lower threshold by 20 points, re-score, set `low_confidence: true`
4. Low-confidence result returned with visible flag in UI

### Path 2 — Human Routing

When automated recovery fails:
- Log to `events` table with `type = 'exception'`, `severity = 'urgent'`
- Exception entry includes: what failed, what was attempted, available data, recommended action
- Exception queue visible to manager role in MissionBrief
- Human acts; override logged to `decision_records` with `decided_by` populated

### Visual Standard
- Degraded mode: orange `⚠ degraded` badge on panel header
- Low confidence: result shown with `⚠ low confidence` flag — not hidden
- Exception queue: severity-coded (urgent = red, high = orange, normal = blue)

### `core/errors.py` exports:
```python
class AIServiceError(Exception): ...
class LowConfidenceError(Exception): ...
class OntologyNotFoundError(Exception): ...
```

---

## What to Preserve Across All Changes

- Design token names — Track A and Track B must stay in sync
- AI model assignments per task — changing a model requires a `DECISION` entry in `build_journey.md`
- Two-path error handling model — both paths must remain functional
- `degraded_mode` and `ai_model` fields on every AI response
- Audit trail — `actions` table `approved_by` and `executed_at` must always be populated on execution
- Prompt structure — system prompt + data-bearing user prompt — never merge into one

---

## Portfolio Intent

This project demonstrates:
- Operational AI architecture — not just "called an API"
- Ontology-first design: the AI reasons about governed objects, not raw tables
- Multi-module progression: each module adds a capability layer on a shared foundation
- Human-in-the-loop execution: approvals, audit trails, and exception routing
- Dual-track delivery: zero-setup HTML demo + production-grade full stack
- Intentional model selection: Sonnet for reasoning tasks, Haiku for summarization
