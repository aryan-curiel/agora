# SaaS Migration Guide

This document maps every concept in the current Claude Code–based Agora system to its equivalent in a hosted SaaS built with **FastAPI + Pydantic AI + React**. It is the primary reference for the re-implementation.

> **PoC scope:** The PoC uses **SQLite** (via SQLModel + aiosqlite) — no external database server, no multi-tenancy, single-user. The schema below is designed to migrate straight to PostgreSQL later with minimal changes: integer PKs swap to UUIDs, `DATETIME` becomes `TIMESTAMPTZ`, and `TEXT` JSON columns become `JSONB`.

---

## Target Stack

| Layer | Technology | Rationale |
|---|---|---|
| Backend API | FastAPI | Async-first, OpenAPI auto-docs, native Pydantic integration |
| Agent framework | Pydantic AI | Structured agent outputs, model-agnostic, type-safe |
| LLM routing | OpenRouter | Single API key for Anthropic models, easy tier switching |
| Database | **SQLite** (via SQLModel + aiosqlite) | Zero-config, file-based, ships with Python; migrates to Postgres later |
| ORM | SQLModel | Combines SQLAlchemy + Pydantic — single model definition for DB and API |
| Auth | None (PoC) | Single-user; add JWT auth before multi-user launch |
| Frontend | React + Vite | SPA, fast, pairs well with FastAPI |
| Job queue | In-process `asyncio` tasks (PoC) | No Redis needed for PoC; swap to Celery/ARQ for production |
| Deployment | Fly.io or Railway | Single container (app + SQLite file on persistent volume) |

> **Upgrade path:** SQLite → PostgreSQL requires changing the connection URL and swapping `TEXT` JSON columns to `JSONB`. SQLModel handles the rest. Add Supabase Auth + RLS when multi-tenancy is needed.

---

## Architecture Comparison

### Current (Claude Code)

```
User → Claude Code session → reads/executes SKILL.md
                           → invokes agents (subagents in same session)
                           → writes markdown files
                           → appends JSONL analytics
```

### SaaS Target (PoC)

```
User → React UI → FastAPI → Pydantic AI orchestrator
                          → LLM calls (OpenRouter / Anthropic)
                          → SQLite via SQLModel (ideas, sessions, scores)
                          → asyncio background tasks (long sessions)
                          → SSE stream (live round output)
```

---

## Concept Mapping

| Agora CLI concept | SaaS equivalent |
|---|---|
| `ideas/{slug}/README.md` | `ideas` table in SQLite |
| `ideas_index.md` | `ideas` table with a list endpoint |
| `ideas/{slug}/sessions/*.md` | `debate_sessions` table + `session_rounds` table |
| `analytics/sessions.jsonl` | `debate_sessions` table (analytics columns included) |
| `analytics/specialists.jsonl` | `specialist_analytics` table |
| `analytics/brainstorms.jsonl` | `brainstorm_sessions` table |
| `analytics/dreamers.jsonl` | `dreamer_analytics` table |
| `.claude/agents/{name}.md` | `agent_definitions` table (system prompt stored as TEXT) |
| `.claude/agents/{name}/MEMORY.md` | `agent_memory` table (per-agent, single user for PoC) |
| `.claude/agents/{name}/PROPOSAL-v*.md` | `improvement_proposals` table |
| `.claude/agents/{name}/CHANGELOG.md` | `agent_versions` table |
| `job-posts/*.md` | `job_posts` table |
| SKILL.md orchestration logic | FastAPI route handlers + Pydantic AI orchestrators |
| Session config in CLAUDE.md | `session_config` table (single row for PoC) |
| Constraint system | `constraints` table linked to `ideas` |

---

## Database Schema

Defined with **SQLModel** — each class is simultaneously a Pydantic model (for API validation) and a SQLAlchemy table (for SQLite). SQLite is the PoC target; switching to PostgreSQL later only requires changing the connection URL and replacing `TEXT` JSON columns with `JSONB`.

Enable foreign key enforcement on every connection:
```python
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
```

### Core Tables

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class Idea(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(unique=True, index=True)
    name: str
    description: Optional[str] = None
    status: str = "active"          # active | archived | completed
    readiness_percentage: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    readiness_scores: list["ReadinessScore"] = Relationship(back_populates="idea")
    constraints: list["Constraint"] = Relationship(back_populates="idea")
    open_questions: list["OpenQuestion"] = Relationship(back_populates="idea")
    notes: list["IdeaNote"] = Relationship(back_populates="idea")


class ReadinessScore(SQLModel, table=True):
    # One row per dimension per idea — updated in place
    idea_id: int = Field(foreign_key="idea.id", primary_key=True)
    dimension: str = Field(primary_key=True)  # problem_statement | target_user | etc.
    score: int = 0                 # 0–10
    notes: Optional[str] = None
    is_na: bool = False
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    idea: Optional[Idea] = Relationship(back_populates="readiness_scores")


class Constraint(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    idea_id: int = Field(foreign_key="idea.id", index=True)
    constraint_text: str
    rationale: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    idea: Optional[Idea] = Relationship(back_populates="constraints")


class OpenQuestion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    idea_id: int = Field(foreign_key="idea.id", index=True)
    question: str
    answered: bool = False
    answered_text: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    idea: Optional[Idea] = Relationship(back_populates="open_questions")


class IdeaNote(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    idea_id: int = Field(foreign_key="idea.id", index=True)
    note_type: Optional[str] = None  # feature | consideration | observation | risk | milestone | origin
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    idea: Optional[Idea] = Relationship(back_populates="notes")


class Proposal(SQLModel, table=True):
    # Brainstorm proposals (not improvement proposals — see ImprovementProposal)
    id: Optional[int] = Field(default=None, primary_key=True)
    idea_id: int = Field(foreign_key="idea.id", index=True)
    brainstorm_session_id: int = Field(foreign_key="brainstormsession.id", index=True)
    horizon: str                     # quick-win | growth-feature | moonshot
    title: str
    description: str
    dreamer: str
    round_number: int
    flagged_by_skeptic: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### Session Tables

```python
class DebateSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    idea_id: int = Field(foreign_key="idea.id", index=True)
    session_number: int
    date: str                        # ISO date string YYYY-MM-DD
    status: str = "running"          # running | completed
    score_before: Optional[int] = None
    score_after: Optional[int] = None
    delta: Optional[int] = None
    rounds_completed: int = 0
    ended_reason: Optional[str] = None  # max_rounds | target_reached
    kpi_score: Optional[float] = None
    kpis_json: Optional[str] = None  # JSON string — use json.loads() to read
    specialists_json: Optional[str] = None  # JSON string — list of specialist names
    created_at: datetime = Field(default_factory=datetime.utcnow)

    rounds: list["SessionRound"] = Relationship(back_populates="session")


class SessionRound(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="debatesession.id", index=True)
    round_number: int
    synthesis: Optional[str] = None
    score_after: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    session: Optional[DebateSession] = Relationship(back_populates="rounds")
    contributions: list["SpecialistContribution"] = Relationship(back_populates="round")


class SpecialistContribution(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    round_id: int = Field(foreign_key="sessionround.id", index=True)
    specialist_name: str
    specialist_version: Optional[str] = None
    response_text: str
    word_count: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    round: Optional[SessionRound] = Relationship(back_populates="contributions")


class SessionKpi(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="debatesession.id", index=True)
    kpi_type: str                    # dimension | question
    dimension: Optional[str] = None
    question_text: Optional[str] = None
    target_score: Optional[int] = None
    before_score: Optional[int] = None
    after_score: Optional[int] = None
    answered: Optional[str] = None   # yes | partial | no
    result: Optional[str] = None     # met | partial | not_met


class BrainstormSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    idea_id: int = Field(foreign_key="idea.id", index=True)
    session_number: int
    date: str
    rounds: int = 3
    proposals_generated: int = 0
    flagged_proposals: int = 0
    dreamer_versions_json: Optional[str] = None  # JSON string
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### Agent & Analytics Tables

```python
class AgentDefinition(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    agent_type: str                  # specialist | dreamer
    version: str
    model: str
    system_prompt: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AgentMemory(SQLModel, table=True):
    # For PoC: one memory record per agent (no org scoping)
    id: Optional[int] = Field(default=None, primary_key=True)
    agent_name: str = Field(unique=True, index=True)
    content: str
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ImprovementProposal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    agent_name: str = Field(index=True)
    current_version: str
    proposed_version: str
    change_type: str                 # patch | minor | major
    session_id: Optional[int] = Field(default=None, foreign_key="debatesession.id")
    status: str = "pending"          # pending | applied
    summary: Optional[str] = None
    observed_issues_json: Optional[str] = None   # JSON string
    proposed_changes_json: Optional[str] = None  # JSON string
    breaking: bool = False
    affected_agents_json: Optional[str] = None   # JSON string — list of agent names
    created_at: datetime = Field(default_factory=datetime.utcnow)
    applied_at: Optional[datetime] = None


class SpecialistAnalytic(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="debatesession.id", index=True)
    specialist_name: str
    version: Optional[str] = None
    adherence: Optional[int] = None
    specificity: Optional[int] = None
    novelty: Optional[int] = None
    responsiveness: Optional[int] = None
    impact: Optional[int] = None
    overall: Optional[float] = None
    word_count_compliance: Optional[bool] = None
    severity: Optional[str] = None
    proposal_id: Optional[int] = Field(default=None, foreign_key="improvementproposal.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DreamerAnalytic(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    brainstorm_session_id: int = Field(foreign_key="brainstormsession.id", index=True)
    dreamer_name: str
    version: Optional[str] = None
    originality: Optional[int] = None
    specificity: Optional[int] = None
    cross_pollination: Optional[int] = None
    horizon_adherence: Optional[int] = None
    overall: Optional[float] = None
    proposals_count: Optional[int] = None
    flagged_count: Optional[int] = None
    word_count_compliance: Optional[bool] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### Database Initialization

```python
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite+aiosqlite:///./agora.db"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

---

## Pydantic AI Agent Design

Each specialist and dreamer maps to a Pydantic AI agent with typed outputs.

### Structured Output Models

```python
from pydantic import BaseModel
from pydantic_ai import Agent
from typing import Optional

class SpecialistResponse(BaseModel):
    specialist_name: str
    response_text: str
    word_count: int

class RoundScore(BaseModel):
    problem_statement: int  # 0-10
    target_user: int
    core_features: int
    tech_stack: int
    go_to_market: int
    key_risks: int
    poc_scope: int
    success_metrics: int
    monetization: Optional[int]  # None = N/A
    budget_estimates: int
    readiness_percentage: int
    synthesis: str
    open_questions: list[str]
    best_answers: dict[str, str]

class BrainstormProposal(BaseModel):
    horizon: str  # quick-win | growth-feature | moonshot
    title: str
    description: str
    dreamer_name: str
    round_number: int

class SkepticGrounding(BaseModel):
    flagged_proposals: list[dict]  # [{title, reason}]
    questions: list[str]           # exactly 2

class LeadSpecialistOutput(BaseModel):
    roster: list[str]              # e.g. ["specialist-skeptic", "specialist-tech-lead", ...]
    reasoning: str
```

### Agent Instantiation Pattern

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel  # works with OpenRouter

def make_specialist(name: str, system_prompt: str, model_id: str) -> Agent:
    model = OpenAIModel(
        model_name=model_id,
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.OPENROUTER_API_KEY,
    )
    return Agent(
        model=model,
        system_prompt=system_prompt,
        result_type=SpecialistResponse,
    )

# Model tier mapping
MODEL_TIERS = {
    "specialist-skeptic":      "anthropic/claude-opus-4-7",
    "specialist-tech-lead":    "anthropic/claude-opus-4-7",
    "specialist-legal":        "anthropic/claude-opus-4-7",
    "dreamer-futurist":        "anthropic/claude-opus-4-7",
    "specialist-finance":      "anthropic/claude-sonnet-4-6",
    "specialist-growth":       "anthropic/claude-sonnet-4-6",
    "specialist-market-analyst": "anthropic/claude-sonnet-4-6",
    "specialist-product-manager": "anthropic/claude-sonnet-4-6",
    "specialist-ux-designer":  "anthropic/claude-sonnet-4-6",
    "dreamer-connector":       "anthropic/claude-sonnet-4-6",
    "dreamer-narrativist":     "anthropic/claude-sonnet-4-6",
    "dreamer-user-advocate":   "anthropic/claude-sonnet-4-6",
    "dreamer-builder":         "anthropic/claude-haiku-4-5-20251001",
}
```

---

## API Endpoints

### Ideas

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/ideas` | List all ideas with readiness scores |
| `POST` | `/api/ideas` | Create new idea |
| `GET` | `/api/ideas/{slug}` | Get full idea detail (scores, constraints, proposals, sessions) |
| `PATCH` | `/api/ideas/{slug}` | Update description, status |
| `POST` | `/api/ideas/{slug}/constraints` | Add constraint |
| `DELETE` | `/api/ideas/{slug}/constraints/{id}` | Remove constraint |
| `POST` | `/api/ideas/{slug}/notes` | Add note |

### Sessions

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/ideas/{slug}/debate` | Start a new debate session |
| `GET` | `/api/ideas/{slug}/sessions` | List all sessions for an idea |
| `GET` | `/api/ideas/{slug}/sessions/{session_id}` | Get full session transcript |
| `POST` | `/api/ideas/{slug}/brainstorm` | Start a new brainstorm session |
| `GET` | `/api/sessions/{session_id}/stream` | SSE stream for live round output |

### Specialists & Improvement

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/sessions/{session_id}/review` | Run specialist review (generates proposals) |
| `GET` | `/api/proposals` | List all pending proposals |
| `POST` | `/api/proposals/{id}/apply` | Apply a proposal to an agent definition |
| `GET` | `/api/agents` | List all agent definitions with versions |
| `GET` | `/api/agents/{name}/memory` | Get agent memory for current org |

### Analytics

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/analytics/sessions` | Session analytics with filters |
| `GET` | `/api/analytics/specialists` | Specialist performance trends |
| `GET` | `/api/analytics/brainstorms` | Brainstorm analytics |
| `GET` | `/api/analytics/ideas/{slug}/progression` | Readiness progression over sessions |

---

## Debate Session Orchestration

The most complex endpoint. Replaces the `agora-run-debate` skill.

```python
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic_ai import Agent
import asyncio

router = APIRouter()

@router.post("/api/ideas/{slug}/debate")
async def start_debate_session(
    slug: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    # 1. Load idea + constraints + open questions
    idea = await db.get_idea_by_slug(slug)
    constraints = await db.get_constraints(idea.id)
    session_config = await db.get_session_config()  # single-row config table

    # 2. Establish KPIs
    kpis = compute_session_kpis(idea.readiness_scores, idea.open_questions)

    # 3. Create session record
    session = await db.create_debate_session(idea.id, score_before=idea.readiness_percentage)

    # 4. Run debate as background asyncio task; stream progress via SSE
    background_tasks.add_task(run_debate_background, session.id, idea, constraints, session_config, kpis)

    return {"session_id": session.id, "status": "running"}


async def run_debate_background(session_id, idea, constraints, session_config, kpis):
    async with AsyncSessionLocal() as db:
        # Lead specialist selects roster
        roster = await lead_specialist.run(idea=idea, constraints=constraints)

        max_rounds = (session_config.max_rounds if idea.readiness_percentage < 30
                      else session_config.max_rounds_partial)

        prior_messages = []
        round_synthesis = None
        for round_num in range(1, max_rounds + 1):
            round_messages = []

            # Specialists run sequentially — each sees prior ones this round
            for specialist_name in roster:
                specialist = get_specialist_agent(specialist_name)
                prompt = build_specialist_prompt(
                    idea=idea,
                    constraints=constraints,
                    prior_rounds=prior_messages[-10:],
                    this_round_so_far=round_messages,
                    round_num=round_num,
                    round_synthesis=round_synthesis,
                )
                response = await specialist.run(prompt)
                round_messages.append({
                    "specialist": specialist_name,
                    "text": response.data.response_text,
                })
                # Push to SSE queue so UI updates in real time
                await push_sse_event(session_id, "specialist_response", {
                    "specialist": specialist_name,
                    "round": round_num,
                    "text": response.data.response_text,
                })

            # Score the round
            score_result = await score_round_agent.run(
                round_messages=round_messages,
                current_scores=idea.readiness_scores,
                constraints=constraints,
            )
            round_synthesis = score_result.data.synthesis

            await db.update_readiness_scores(idea.id, score_result.data.scores)
            await db.create_session_round(session_id, round_num, score_result.data)

            prior_messages.extend(round_messages)

            new_readiness = score_result.data.readiness_percentage
            if new_readiness >= session_config.readiness_target:
                ended_reason = "target_reached"
                break
        else:
            ended_reason = "max_rounds"

        await db.complete_debate_session(session_id, ended_reason, new_readiness, kpis)
        await push_sse_event(session_id, "session_complete", {"score_after": new_readiness})
```

---

## Streaming Output (SSE)

Long-running sessions (30–90 seconds) must stream output to the UI. Use Server-Sent Events:

```python
from fastapi.responses import StreamingResponse
from asyncio import Queue

session_streams: dict[str, Queue] = {}

@router.get("/api/sessions/{session_id}/stream")
async def stream_session(session_id: str):
    queue = session_streams.get(session_id)

    async def event_generator():
        while True:
            event = await queue.get()
            if event is None:
                break
            yield f"data: {event.json()}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

UI subscribes to the stream as soon as a session is started and renders specialist panels as they arrive.

---

## Multi-Tenancy

**PoC: no multi-tenancy.** The SQLite schema is single-user — no `org_id` column anywhere. All ideas and sessions belong to the single local user.

When upgrading to PostgreSQL for multi-user launch:
1. Add `org_id UUID REFERENCES orgs(id)` to `ideas`, `agent_memory`, and `debate_sessions`
2. Add a `UNIQUE(org_id, slug)` constraint to `ideas`
3. Enable Supabase RLS policies:

```sql
-- Ideas only visible within org
ALTER TABLE ideas ENABLE ROW LEVEL SECURITY;
CREATE POLICY "org_isolation" ON ideas
    USING (org_id = auth.jwt() ->> 'org_id');

-- Agent memory is org-scoped
ALTER TABLE agent_memory ENABLE ROW LEVEL SECURITY;
CREATE POLICY "org_memory_isolation" ON agent_memory
    USING (org_id = auth.jwt() ->> 'org_id');
```

Agent **definitions** (system prompts) stay global — shared across all orgs. Agent **memory** becomes org-scoped — each org's specialists accumulate independent cross-session patterns.

---

## Key Migration Decisions

### 1. Agent memory scope

In the CLI, memory is stored per-project (one `MEMORY.md` per agent). In the PoC SaaS:
- **PoC:** One memory record per agent in `agent_memory` table — global, no user scoping.
- **Production:** Per-org memory — each org's specialists evolve independently. Add `org_id` to `agent_memory` and a `UNIQUE(org_id, agent_name)` constraint.

### 2. Agent definition management

In the CLI, system prompts are edited directly in `.md` files. In SaaS:
- Store system prompts in the database
- Provide an admin UI for editing (with version history)
- Or keep them in a config repo and deploy via migration

### 3. Brainstorm parallelism

In the CLI, all 5 dreamers run in parallel within a round via multiple `Agent` tool calls. In the API, use `asyncio.gather()`:

```python
async def run_brainstorm_round(dreamers, idea, history, horizon_assignments, round_num):
    tasks = [
        dreamer_agent.run(
            build_dreamer_prompt(idea, history, horizon_assignments[name], round_num)
        )
        for name, dreamer_agent in dreamers.items()
    ]
    results = await asyncio.gather(*tasks)
    return {name: result.data for name, result in zip(dreamers.keys(), results)}
```

### 4. Session configuration

In the CLI, session defaults are in `CLAUDE.md` and per-idea overrides in the README. In the PoC:
- Store defaults in a single-row `session_config` table (seeded on `init_db`)
- Allow per-idea overrides as a `session_overrides_json` TEXT column on `ideas`
- Production: move defaults to an org settings table, expose both in the UI as editable fields

### 5. Proposal application

In the CLI, `agora-apply-specialist-update` edits a Markdown file. In SaaS:
- Create a new `agent_definitions` row with the new version
- Mark old row as inactive
- The system always uses the latest active version per agent name

---

## UI Screens

| Screen | Purpose |
|---|---|
| Dashboard | All ideas with readiness progress bars; recent sessions |
| Idea Detail | Full readiness breakdown, constraints, proposals, session history |
| Add Idea | Wizard: description → 9 dimension questions → initial scores |
| Debate Session | Live streaming view of round-by-round specialist panels; milestone updates |
| Brainstorm Session | Live streaming view of parallel dreamer outputs; proposals by horizon |
| Session Report | Full transcript with scores, KPI results, recommendations |
| Proposals | Ranked list of pending improvement proposals with apply buttons |
| Agent Admin | List of agents with versions, performance history, memory viewer |
| Analytics | Charts: score progression, specialist quality trends, horizon distribution |

---

## Feature Parity Checklist

| Agora CLI Feature | SaaS Status |
|---|---|
| Add idea with 9-question wizard | Must implement |
| Readiness scoring (10 dimensions) | Must implement |
| Constraint system | Must implement |
| Lead specialist roster selection | Must implement |
| Sequential debate rounds | Must implement |
| Parallel brainstorm dreamers | Must implement |
| Skeptic grounding (brainstorm) | Must implement |
| Session KPIs (before/after) | Must implement |
| Adaptive round count by readiness | Must implement |
| Session termination (max rounds / target) | Must implement |
| Session reports (full transcript) | Must implement |
| Analytics JSONL → DB records | Must implement |
| Agent memory per-session | Must implement |
| Specialist review + proposals | Should implement |
| Proposal apply with version bump | Should implement |
| Cascade breaking change handling | Should implement |
| Hire specialists (job posts) | Nice to have |
| Build specialist from job post | Nice to have |
| Streamlit analytics dashboard | Replace with React charts |
| Session streaming (SSE) | Must implement (no SSE equivalent in CLI) |
| Multi-tenancy + auth | **Not in PoC** — single user, no auth; add for production |
| Shareable session links | Nice to have (not in CLI) |
