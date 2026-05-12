---
name: agora-write-report
description: Writes a markdown session report after a debate completes. Invoked automatically by agora-run-debate. Not for direct user invocation.
user-invocable: false
version: 1.1.0
model: haiku
author: Aryan Curiel
---

## Write a session report

The caller passes session data including [SESSION_KPIS] and [KPI_RESULTS] from the run-debate skill.

Create ideas/{slug}/sessions/{slug}-session-{n}-{YYYYMMDD}.md with this structure:

```markdown
# {Idea Name} — Session {n} Report

**Date:** {YYYY-MM-DD}
**Session:** {n}
**Readiness:** {before}% → {after}% (+{delta}%)
**Rounds completed:** {n}
**Ended because:** {reason}
**Specialists:** {comma-separated specialist names}

---

## Constraints

{If the idea had constraints, include this section. Otherwise omit it entirely.}

| Constraint | Rationale | Override Proposed? |
|---|---|---|
| {constraint} | {rationale} | Yes — {specialist}: {justification} / No |

---

## Session KPIs

**KPI Score: {kpi_score × 100}%**

### Dimension Targets

| Dimension | Target | Before | After | Result |
|---|---|---|---|---|
| {dimension} | {target}/10 | {before}/10 | {after}/10 | Met / Partial / Not met |
...

### Key Questions

| Question | Answered? |
|---|---|
| {question text} | Yes / Partial / No |
...

---

## Readiness Breakdown

| Dimension | Before | After | Change |
|---|---|---|---|
| Problem statement | x/10 | x/10 | +x |
...

---

## Synthesis

{synthesis from final round agora-meta-specialist output}

---

## Open Questions

{numbered list of remaining open questions}

---

## Best Answers Established

{best_answers dict formatted as dimension: answer pairs}

---

## Full Transcript

### Round {n}

#### {Specialist Name}
{full message content}

---

#### {Specialist Name}
{full message content}

---

*[repeat for all agents and rounds]*

---

## Recommendations for Next Session

Based on the lowest-scoring dimensions, the next session should focus on:
1. {lowest dim}: {specific suggestion based on open questions}
2. {second lowest}: {specific suggestion}
3. {third lowest}: {specific suggestion}
```

After writing the file, return the filename to the caller.
