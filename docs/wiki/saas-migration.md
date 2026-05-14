# SaaS Migration Guide

This document maps every concept in the current Claude Code–based Agora system to its equivalent in a hosted SaaS built with **FastAPI + Pydantic AI + React**. It is the primary reference for the re-implementation.

---

## Target Stack

| Layer | Technology | Rationale |
|---|---|---|
| Backend API | FastAPI | Async-first, OpenAPI auto-docs, native Pydantic integration |
| Agent framework | Pydantic AI | Structured agent outputs, model-agnostic, type-safe |
| LLM routing | OpenRouter | Single API key for Anthropic models, easy tier switching |
| Database | PostgreSQL (via Supabase) | Replaces markdown files; multi-tenant safe, queryable |
| Auth | Supabase Auth | JWT, OAuth, Row Level Security for multi-tenancy |
| Frontend | React + Vite | SPA, fast, pairs well with FastAPI |
| Storage | Supabase Storage or S3 | Session report files |
| Job queue | BullMQ + Redis (or Celery) | Long-running debate/brainstorm sessions |
| Deployment | Fly.io or Railway | Simple container deployment |

---

## Architecture Comparison

### Current (Claude Code)

```
User → Claude Code session → reads/executes SKILL.md
                           → invokes agents (subagents in same session)
                           → writes markdown files
                           → appends JSONL analytics
```

### SaaS Target

```
User → React UI → FastAPI → Pydantic AI orchestrator
                          → LLM calls (OpenRouter / Anthropic)
                          → PostgreSQL (ideas, sessions, scores)
                          → background job queue (long sessions)
                          → streaming WebSocket or SSE (live round output)
```

---

## Concept Mapping

| Agora CLI concept | SaaS equivalent |
|---|---|
| `ideas/{slug}/README.md` | `ideas` table in PostgreSQL |
| `ideas_index.md` | `ideas` table with a list endpoint |
| `ideas/{slug}/sessions/*.md` | `sessions` table + `session_rounds` table |
| `analytics/sessions.jsonl` | `session_analytics` table (or same `sessions` table with analytics columns) |
| `analytics/specialists.jsonl` | `specialist_analytics` table |
| `analytics/brainstorms.jsonl` | `brainstorm_sessions` table |
| `analytics/dreamers.jsonl` | `dreamer_analytics` table |
| `.claude/agents/{name}.md` | Agent definition stored in DB or config files; model deployed as Pydantic AI agent |
| `.claude/agents/{name}/MEMORY.md` | `agent_memory` table (per-agent, per-user or per-org) |
| `.claude/agents/{name}/PROPOSAL-v*.md` | `improvement_proposals` table |
| `.claude/agents/{name}/CHANGELOG.md` | `agent_versions` table |
| `job-posts/*.md` | `job_posts` table |
| SKILL.md orchestration logic | FastAPI route handlers + Pydantic AI orchestrators |
| Session config in CLAUDE.md | `session_config` table or org-level settings |
| Constraint system | `constraints` table linked to `ideas` |

---

## Database Schema

### Core Tables

```sql
-- Ideas
CREATE TABLE ideas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES orgs(id),
    slug TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'active',  -- active | archived | completed
    readiness_percentage INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(org_id, slug)
);

-- Readiness dimension scores (one row per dimension per idea — updated in place)
CREATE TABLE readiness_scores (
    idea_id UUID REFERENCES ideas(id),
    dimension TEXT NOT NULL,  -- problem_statement | target_user | etc.
    score INTEGER NOT NULL DEFAULT 0,  -- 0–10
    notes TEXT,
    is_na BOOLEAN DEFAULT false,
    updated_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (idea_id, dimension)
);

-- Constraints
CREATE TABLE constraints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    idea_id UUID REFERENCES ideas(id),
    constraint_text TEXT NOT NULL,
    rationale TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Open questions per idea
CREATE TABLE open_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    idea_id UUID REFERENCES ideas(id),
    question TEXT NOT NULL,
    answered BOOLEAN DEFAULT false,
    answered_text TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Notes on ideas
CREATE TABLE idea_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    idea_id UUID REFERENCES ideas(id),
    note_type TEXT,  -- feature | consideration | observation | risk | milestone | origin
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Brainstorm proposals
CREATE TABLE proposals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    idea_id UUID REFERENCES ideas(id),
    session_id UUID REFERENCES brainstorm_sessions(id),
    horizon TEXT NOT NULL,  -- quick-win | growth-feature | moonshot
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    dreamer TEXT NOT NULL,
    round_number INTEGER NOT NULL,
    flagged_by_skeptic BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now()
);
```

### Session Tables

```sql
-- Debate sessions
CREATE TABLE debate_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    idea_id UUID REFERENCES ideas(id),
    session_number INTEGER NOT NULL,
    date DATE NOT NULL,
    status TEXT DEFAULT 'running',  -- running | completed
    score_before INTEGER,
    score_after INTEGER,
    delta INTEGER,
    rounds_completed INTEGER DEFAULT 0,
    ended_reason TEXT,  -- max_rounds | target_reached
    kpi_score FLOAT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Individual rounds within a session
CREATE TABLE session_rounds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES debate_sessions(id),
    round_number INTEGER NOT NULL,
    synthesis TEXT,
    score_after INTEGER,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Per-specialist contribution per round
CREATE TABLE specialist_contributions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    round_id UUID REFERENCES session_rounds(id),
    specialist_name TEXT NOT NULL,
    specialist_version TEXT,
    response_text TEXT NOT NULL,
    word_count INTEGER,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Session KPI targets
CREATE TABLE session_kpis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES debate_sessions(id),
    kpi_type TEXT NOT NULL,  -- dimension | question
    dimension TEXT,
    question_text TEXT,
    target_score INTEGER,
    before_score INTEGER,
    after_score INTEGER,
    answered TEXT,  -- yes | partial | no (for questions)
    result TEXT     -- met | partial | not_met (for dimensions)
);

-- Brainstorm sessions
CREATE TABLE brainstorm_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    idea_id UUID REFERENCES ideas(id),
    session_number INTEGER NOT NULL,
    date DATE NOT NULL,
    rounds INTEGER DEFAULT 3,
    proposals_generated INTEGER DEFAULT 0,
    flagged_proposals INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now()
);
```

### Agent & Analytics Tables

```sql
-- Agent definitions (replaces .claude/agents/*.md)
CREATE TABLE agent_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    agent_type TEXT NOT NULL,  -- specialist | dreamer
    version TEXT NOT NULL,
    model TEXT NOT NULL,
    system_prompt TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Agent memory (replaces MEMORY.md files; org-scoped for multi-tenancy)
CREATE TABLE agent_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES orgs(id),
    agent_name TEXT NOT NULL,
    content TEXT NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(org_id, agent_name)
);

-- Improvement proposals (replaces PROPOSAL-v*.md)
CREATE TABLE improvement_proposals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name TEXT NOT NULL,
    current_version TEXT NOT NULL,
    proposed_version TEXT NOT NULL,
    change_type TEXT NOT NULL,  -- patch | minor | major
    session_id UUID REFERENCES debate_sessions(id),
    status TEXT DEFAULT 'pending',  -- pending | applied
    summary TEXT,
    observed_issues JSONB,
    proposed_changes JSONB,
    breaking BOOLEAN DEFAULT false,
    affected_agents TEXT[],
    created_at TIMESTAMPTZ DEFAULT now(),
    applied_at TIMESTAMPTZ
);

-- Specialist performance analytics
CREATE TABLE specialist_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES debate_sessions(id),
    specialist_name TEXT NOT NULL,
    version TEXT,
    adherence INTEGER,
    specificity INTEGER,
    novelty INTEGER,
    responsiveness INTEGER,
    impact INTEGER,
    overall FLOAT,
    word_count_compliance BOOLEAN,
    severity TEXT,
    proposal_id UUID REFERENCES improvement_proposals(id),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Dreamer performance analytics
CREATE TABLE dreamer_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brainstorm_session_id UUID REFERENCES brainstorm_sessions(id),
    dreamer_name TEXT NOT NULL,
    version TEXT,
    originality INTEGER,
    specificity INTEGER,
    cross_pollination INTEGER,
    horizon_adherence INTEGER,
    overall FLOAT,
    proposals_count INTEGER,
    flagged_count INTEGER,
    word_count_compliance BOOLEAN,
    created_at TIMESTAMPTZ DEFAULT now()
);
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
from fastapi import APIRouter, Depends
from pydantic_ai import Agent
import asyncio

router = APIRouter()

@router.post("/api/ideas/{slug}/debate")
async def start_debate_session(slug: str, org: Org = Depends(get_org)):
    # 1. Load idea + constraints + open questions
    idea = await db.get_idea(org.id, slug)
    constraints = await db.get_constraints(idea.id)
    session_config = org.session_config

    # 2. Establish KPIs
    kpis = compute_session_kpis(idea.readiness_scores, idea.open_questions)

    # 3. Create session record
    session = await db.create_debate_session(idea.id, score_before=idea.readiness_percentage)

    # 4. Lead specialist selects roster
    roster = await lead_specialist.run(idea=idea, constraints=constraints)

    # 5. Determine max rounds
    max_rounds = (session_config.max_rounds if idea.readiness_percentage < 30
                  else session_config.max_rounds_partial)

    # 6. Run rounds
    prior_messages = []
    for round_num in range(1, max_rounds + 1):
        round_messages = []

        # Specialists run sequentially — each sees prior ones this round
        for specialist_name in roster:
            specialist = get_specialist_agent(specialist_name, org.id)
            prompt = build_specialist_prompt(
                idea=idea,
                constraints=constraints,
                prior_rounds=prior_messages[-10:],
                this_round_so_far=round_messages,
                round_num=round_num,
                round_synthesis=round_synthesis if round_num > 1 else None,
            )
            response = await specialist.run(prompt)
            round_messages.append({
                "specialist": specialist_name,
                "text": response.data.response_text
            })
            # Stream to client via SSE
            await stream_event(session.id, "specialist_response", {
                "specialist": specialist_name,
                "round": round_num,
                "text": response.data.response_text
            })

        # Score the round
        score_result = await score_round_agent.run(
            round_messages=round_messages,
            current_scores=idea.readiness_scores,
            constraints=constraints,
        )
        round_synthesis = score_result.data.synthesis

        # Update scores
        await db.update_readiness_scores(idea.id, score_result.data.scores)
        await db.create_session_round(session.id, round_num, score_result.data)

        prior_messages.extend(round_messages)

        # Check termination
        new_readiness = score_result.data.readiness_percentage
        if new_readiness >= session_config.readiness_target:
            ended_reason = "target_reached"
            break
    else:
        ended_reason = "max_rounds"

    # 7. Finalize session
    await db.complete_debate_session(session.id, ended_reason, new_readiness, kpis)
    return {"session_id": str(session.id), "score_after": new_readiness}
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

All idea, session, and agent memory data is scoped to an `org_id`. Row Level Security (Supabase):

```sql
-- Ideas only visible within org
ALTER TABLE ideas ENABLE ROW LEVEL SECURITY;
CREATE POLICY "org_isolation" ON ideas
    USING (org_id = auth.jwt() ->> 'org_id');

-- Agent memory is org-scoped (each org gets independent specialist memory)
ALTER TABLE agent_memory ENABLE ROW LEVEL SECURITY;
CREATE POLICY "org_memory_isolation" ON agent_memory
    USING (org_id = auth.jwt() ->> 'org_id');
```

Agent **definitions** (system prompts) are global — shared across all orgs. Agent **memory** is org-scoped — each org's specialists accumulate independent cross-session patterns.

---

## Key Migration Decisions

### 1. Agent memory scope

In the CLI, memory is stored per-project (one set of `MEMORY.md` files). In SaaS:
- **Option A (recommended):** Per-org memory — each org's specialists evolve independently based on their sessions.
- **Option B:** Global memory — all orgs share a single memory that improves from all sessions combined.

Recommendation: start with per-org, add opt-in global memory pool later.

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

In the CLI, session defaults are in `CLAUDE.md` and per-idea overrides in the README. In SaaS:
- Store defaults in org settings table
- Allow per-idea overrides in the ideas table
- Expose both in the UI as editable fields

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
| Multi-tenancy + auth | Must implement (not in CLI) |
| Shareable session links | Must implement (not in CLI) |
