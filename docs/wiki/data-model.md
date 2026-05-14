# Data Model

All persistent state in Agora is Markdown or JSONL. This document specifies every file schema.

---

## Idea File — `ideas/{slug}/README.md`

The canonical state of an idea. Updated after every debate round.

### Full Schema

```markdown
# {Idea Name}

## ID
{slug}

## Description
{Free-form description — can be multiple paragraphs. Specialists receive this in Round 1.}

## Status
active | archived | completed

## Constraints

| Constraint | Rationale |
|---|---|
| {constraint text} | {why it exists} |

## Readiness Score
{N}%

## Readiness Breakdown

| Dimension | Score | Notes |
|---|---|---|
| Problem statement | {N}/10 | {What is known / what is missing} |
| Target user       | {N}/10 | ... |
| Core features     | {N}/10 | ... |
| Tech stack        | {N}/10 | ... |
| Go to market      | {N}/10 | ... |
| Key risks         | {N}/10 | ... |
| PoC scope         | {N}/10 | ... |
| Success metrics   | {N}/10 | ... |
| Monetization      | {N}/10 | ... N/A for personal/OSS |
| Budget estimates  | {N}/10 | ... |

## Open Questions

- {question 1}
- {question 2}
...

## Notes

| Date | Type | Note |
|---|---|---|
| {YYYY-MM-DD} | {feature|consideration|proposal|observation|risk|origin|milestone} | {text} |

## Proposals

*Last updated: {YYYY-MM-DD} (Brainstorm Session {n})*

### Quick Wins (0–3 months)
- **{title}** (Session {n}): {1-sentence description}

### Growth Features (3–12 months)
- **{title}** (Session {n}): {1-sentence description}

### Moonshots (1+ year)
- **{title}** (Session {n}): {1-sentence description}

## Current Best Answers

**Problem statement**: {answer}
**Target user**: {answer}
**Core features**: {answer}
**Tech stack**: {answer}
**Go to market**: {answer}
**Key risks**: {answer}
**PoC scope**: {answer}
**Success metrics**: {answer}
**Monetization**: {answer}
**Budget estimates**: {answer}

## Session History

| Session | Date | Score Before | Score After | Rounds | Report |
|---|---|---|---|---|---|
| 1 | {YYYY-MM-DD} | {N}% | {N}% | {n} | ideas/{slug}/sessions/{filename} |

## Session overrides
{Optional — overrides CLAUDE.md defaults for this idea only}
max_rounds: 4
readiness_target: 90
```

### Readiness Score Calculation

```
readiness_percentage = round(mean([d.score for d in dimensions]) / 10 * 100)
```

Where `dimensions` = all 10 dimensions. Each dimension is scored 0–10.

If a dimension is `N/A` (e.g., monetization for a personal/OSS project), it is excluded from the mean calculation.

---

## Ideas Index — `ideas_index.md`

Master index tracking all ideas. Updated by add-idea, run-debate, and brainstorm skills.

```markdown
| ID | Name | Score | Status | Sessions | Brainstorms | Last Updated |
|---|---|---|---|---|---|---|
| agora | Agora | 85% | active | 1 | 1 | 2026-05-12 |
| flavour-graph | Flavour Graph | 85% | active | 3 | 0 | 2026-05-11 |
| agora-saas | Agora SaaS | 24% | active | 0 | 1 | 2026-05-12 |
```

Columns:
- `ID` — the slug used in all skill arguments and file paths
- `Name` — display name
- `Score` — current readiness percentage
- `Status` — `active` | `archived` | `completed`
- `Sessions` — count of debate sessions
- `Brainstorms` — count of brainstorm sessions
- `Last Updated` — date of most recent change

---

## Debate Session Report — `ideas/{slug}/sessions/{slug}-session-{n}-{YYYYMMDD}.md`

Written by `agora-write-report`. Full transcript + scores + recommendations.

```markdown
# {Idea Name} — Session {n}

**Date:** {YYYY-MM-DD}
**Session:** {n}
**Specialists:** {specialist-name} v{version}, ..., specialist-skeptic v{version}
**Readiness before:** {X}%
**Readiness after:** {Y}%
**Rounds:** {n}
**Ended because:** max_rounds | target_reached

---

## Session KPIs

**Readiness target:** {X}% → {estimated Y}%

### Dimension Targets
| Dimension | Before | Target | After | Result |
|---|---|---|---|---|
| {dim} | {N}/10 | {N}/10 | {N}/10 | Met / Partial / Not met |

### Key Questions
| Question | Answered |
|---|---|
| {question} | Yes / Partial / No |

**KPI Score:** {X}% achieved

---

## Readiness Breakdown

| Dimension | Before | After | Delta |
|---|---|---|---|
| Problem statement | {N}/10 | {N}/10 | +{N} |
...

**Overall:** {X}% → {Y}% (+{Z}%)

---

## Synthesis

{2–3 sentence synthesis of what was established this session}

---

## Open Questions

1. {question}
2. {question}
...

---

## Best Answers Established

**Problem statement:** {answer}
**Target user:** {answer}
...

---

## Full Transcript

### Round 1

┌─ Specialist Name ───────────────────────────────────────┐
│                                                          │
│ {full specialist response}                               │
│                                                          │
└──────────────────────────────────────────────────────────┘

┌─ The Skeptic ────────────────────────────────────────────┐
│ ...                                                       │
└──────────────────────────────────────────────────────────┘

**Round 1 Score:** {X}%

### Round 2
...

---

## Recommendations

Focus for next session:
- **{dim}** ({N}/10): {what needs to be addressed}
- **{dim}** ({N}/10): ...
```

---

## Brainstorm Session Report — `ideas/{slug}/sessions/{slug}-brainstorm-{n}-{YYYYMMDD}.md`

Written by `agora-write-brainstorm-report`.

```markdown
# {Idea Name} — Brainstorm Session {n}

**Date:** {YYYY-MM-DD}
**Session:** {n}
**Dreamers:** The Futurist · The Builder · The User Advocate · The Connector · The Narrativist
**Rounds:** 3
**Proposals generated:** {total}

---

## Proposals by Horizon

### Quick Wins (0–3 months)
| Title | Dreamer | Round | Description |
|---|---|---|---|
| {title} | The {Name} | {n} | {description} |

### Growth Features (3–12 months)
...

### Moonshots (1+ year)
...

---

## Skeptic Grounding

### After Round 2
**Skeptic Flags:**
- **{Proposal title}**: {one sentence why it's broken/exists/false premise}

**Questions:**
1. {question?}
2. {question?}

### After Round 3
...

---

## Full Transcript

### Round 1

┌─ The Futurist ─────────────────────────────────────────┐
│ {full response}                                         │
└─────────────────────────────────────────────────────────┘

┌─ The Builder ──────────────────────────────────────────┐
│ ...                                                     │
└─────────────────────────────────────────────────────────┘

{and so on for all 5 dreamers, in canonical order}

### Round 2
...

### Round 3
...
```

---

## Proposal File — `.claude/agents/{name}/PROPOSAL-v{version}.md`

```yaml
---
specialist: {specialist-name}
current-version: {MAJOR.MINOR.PATCH}
proposed-version: {MAJOR.MINOR.PATCH}
change-type: patch | minor | major
session: ideas/{slug}/sessions/{filename}
date: {YYYY-MM-DD}
status: pending | applied
applied-date: {YYYY-MM-DD}   # only present after application
---
```

```markdown
## Proposed Changes to {specialist-name}

### Summary
{1–2 sentences: why the agent underperformed and what the fix addresses}

### Observed Issues
- **[minor|moderate|major]** {Description of observed behavior and why it is a problem.}
  *Evidence: Round {n} — "{quote or paraphrase from transcript}"*

### Proposed Skill Changes

#### Change {n}: {Short title}

**Current instruction:**
```
{exact text block to replace}
```

**Proposed instruction:**
```
{replacement text}
```

**Rationale:** {Why this change addresses the observed issue}

### Breaking Change Analysis
- **Breaking:** yes | no
- **Affected specialists:** {list or "none"}
- **What breaks:** {description or "n/a"}

### Recommended Testing
{One sentence on how to verify the change worked in the next session}

### Architectural Notes  *(major only)*
{Recommendation on whether /knowledge-architect should be consulted}
```

---

## Agent CHANGELOG — `.claude/agents/{name}/CHANGELOG.md`

```markdown
# Changelog — {specialist-name}

## [1.1.1] — 2026-05-11

### Fixed
- Added explicit instruction to name specific subreddits when proposing distribution channels.

**Source:** Proposal `PROPOSAL-v1.1.1.md` — session `ideas/flavour-graph/sessions/...`

---

## [1.1.0] — 2026-05-08

### Changed
- Added gross margin >30% check to monetization output.

**Source:** Proposal `PROPOSAL-v1.1.0.md` — session `ideas/agora/sessions/...`

---
```

---

## Agent Memory — `.claude/agents/{name}/MEMORY.md`

Free-form. Agent-curated. No fixed schema — each agent structures it according to their role. Rules:

- No idea-specific details (those live in `ideas/{slug}/`)
- Concise — compress rather than accumulate
- Merge new observations; strengthen what proved true, remove what was contradicted
- Written by the agent at the end of each turn (only if new patterns emerged)

Example (Skeptic memory):
```markdown
# Memory — The Skeptic

*Last updated: 2026-05-11*

## High-Frequency Assumption Failures
- Data licensing assumptions are almost always skipped and always matter
- "First mover advantage" claims are consistently undefended

## Most Effective Challenge Angles
- Ask who the user switches FROM, not just who they are
- Ask what happens when inference costs drop to zero

## Systematically Overconfident Domains
- Consumer apps: founders underestimate retention cliffs
- B2B SaaS: founders underestimate sales cycle length
```

---

## Job Post — `job-posts/{role-slug}.md`

```markdown
# Job Post: {Role Title}

## Why we need this specialist
{Gap observed — which sessions, which dimensions}

## Role description
{What this specialist contributes to debate sessions}

## Expected output per turn
{Specific content and format}

## Session coverage
{Which readiness dimensions primarily addressed}

## Selection criteria
{When agora-lead-specialist should pick this over others}
```

---

## File Naming Conventions

| File type | Pattern | Example |
|---|---|---|
| Idea README | `ideas/{slug}/README.md` | `ideas/flavour-graph/README.md` |
| Debate session | `ideas/{slug}/sessions/{slug}-session-{n}-{YYYYMMDD}.md` | `ideas/flavour-graph/sessions/flavour-graph-session-3-20260511.md` |
| Brainstorm session | `ideas/{slug}/sessions/{slug}-brainstorm-{n}-{YYYYMMDD}.md` | `ideas/agora-saas/sessions/agora-saas-brainstorm-1-20260512.md` |
| Proposal | `.claude/agents/{name}/PROPOSAL-v{version}.md` | `.claude/agents/specialist-skeptic/PROPOSAL-v1.1.2.md` |
| Changelog | `.claude/agents/{name}/CHANGELOG.md` | `.claude/agents/specialist-finance/CHANGELOG.md` |
| Memory | `.claude/agents/{name}/MEMORY.md` | `.claude/agents/dreamer-futurist/MEMORY.md` |
| Job post | `job-posts/{slug}.md` | `job-posts/specialist-devrel.md` |
| Analytics | `analytics/{type}.jsonl` | `analytics/sessions.jsonl` |

All slugs: lowercase, hyphen-separated, no spaces.
