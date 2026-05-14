# Agora — System Wiki

> **Purpose of this wiki:** Full reference documentation for the Agora multi-agent debate system. Intended as the canonical specification for building a SaaS API and UI version using Pydantic AI.

---

## What is Agora?

Agora is a multi-agent AI debate system that develops raw ideas into fully specified PoC/MVP plans. Users describe an idea; specialist agents with distinct goals debate it across multiple rounds; a readiness score across 10 dimensions tracks progress. When an idea reaches 85% readiness, it is considered fully planned and ready to build.

The current implementation runs entirely inside **Claude Code** as a set of Skills and Agent definitions — no external servers, no databases, all state stored as Markdown files. The goal of this wiki is to document that system precisely enough to re-implement it as a hosted SaaS API and web UI using Pydantic AI.

---

## Wiki Contents

| Document | What it covers |
|---|---|
| **[Architecture](architecture.md)** | System overview, component relationships, execution model |
| **[Agents](agents.md)** | All 13 agents — 8 debate specialists + 5 brainstorm dreamers — with full behavioral specs |
| **[Skills](skills.md)** | All 18 workflow skills with triggers, inputs, outputs, and internal logic |
| **[Workflow: Debate](workflows/debate.md)** | End-to-end debate session flow with sequence diagrams |
| **[Workflow: Brainstorm](workflows/brainstorm.md)** | End-to-end brainstorm session flow with sequence diagrams |
| **[Workflow: Continuous Improvement](workflows/improvement.md)** | Review → Propose → Apply → Hire loop |
| **[Data Model](data-model.md)** | All file schemas: ideas, sessions, analytics JSONL records |
| **[Scoring System](scoring.md)** | 10 readiness dimensions, scoring rubric, session KPI framework |
| **[Analytics](analytics.md)** | JSONL tracking schemas, dashboard, metrics definitions |
| **[SaaS Migration Guide](saas-migration.md)** | How to port this system to FastAPI + Pydantic AI + React |

---

## Quick-Reference: Key Numbers

| Parameter | Value |
|---|---|
| Readiness dimensions | 10 |
| Readiness target | 85% |
| Max rounds (new idea, readiness < 30%) | 3 |
| Max rounds (partial, readiness ≥ 30%) | 2 |
| Max brainstorm rounds | 3 (always all run) |
| Max roster size per session | 4 (including Skeptic) |
| Debate specialists available | 8 |
| Brainstorm dreamers | 5 |
| Specialist word limit per turn | 250–400 words |
| Agent versioning scheme | Semantic (MAJOR.MINOR.PATCH) |

---

## Quick-Reference: Component Map

```
Skills (orchestrators)             Agents (workers)
──────────────────────────         ──────────────────────────────────────
agora-run-debate              →    specialist-skeptic       (Opus 4.7)
                              →    specialist-tech-lead     (Opus 4.7)
                              →    specialist-legal         (Opus 4.7)
                              →    specialist-finance       (Sonnet 4.6)
                              →    specialist-growth        (Sonnet 4.6)
                              →    specialist-market-analyst(Sonnet 4.6)
                              →    specialist-product-manager(Sonnet 4.6)
                              →    specialist-ux-designer   (Sonnet 4.6)

agora-brainstorm              →    dreamer-futurist         (Opus 4.7)
                              →    dreamer-builder          (Haiku 4.5)
                              →    dreamer-user-advocate    (Sonnet 4.6)
                              →    dreamer-connector        (Sonnet 4.6)
                              →    dreamer-narrativist      (Sonnet 4.6)

agora-run-debate (sub-skills) →    agora-lead-specialist    (selects roster)
                              →    agora-score-round        (scores after each round)
                              →    agora-write-report       (writes session file)

agora-brainstorm (sub-skills) →    agora-write-brainstorm-report
                              →    specialist-skeptic       (grounding after rounds 2–3)

agora-review-specialists      reads session transcript → writes PROPOSAL-v*.md
agora-apply-specialist-update reads PROPOSAL → patches agent definition + CHANGELOG
agora-hire-specialists        reads sessions → writes job-posts/
agora-build-specialist        reads job-post → writes new agent definition
```

---

## System Invariants

These rules hold throughout the entire system and must be preserved in any re-implementation:

1. **All state is in files.** Ideas in `ideas/{slug}/README.md`, index in `ideas_index.md`, sessions in `ideas/{slug}/sessions/`, analytics in `analytics/*.jsonl`.
2. **Specialists debate sequentially.** Each specialist sees what the prior ones in the same round wrote before generating its response.
3. **Dreamers run in parallel.** All 5 dreamers in a brainstorm round are invoked concurrently; cross-pollination only happens between rounds.
4. **Constraints are hard.** Any specialist can propose overriding a constraint only with the explicit `⚠ CONSTRAINT OVERRIDE:` marker and a one-sentence justification.
5. **Skeptic always runs.** The Skeptic is always in the debate roster. In brainstorms, the Skeptic grounds after rounds 2 and 3 only.
6. **Scores accumulate, never reset.** Readiness scores are updated in the idea README after every round and never decrease retroactively.
7. **Analytics are append-only.** All `.jsonl` files are written with append — never overwritten.
8. **Version bumps are semantic.** Patch = wording only, Minor = behavior change, Major = output format change that could break callers.
