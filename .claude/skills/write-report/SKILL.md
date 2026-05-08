---
name: write-report
description: Writes a markdown session report after a debate completes. Invoked automatically by run-debate. Not for direct user invocation.
user-invocable: false
version: 1.0.0
---

## Write a session report

Create ideas/{slug}/sessions/{slug}-session-{n}-{YYYYMMDD}.md with this structure:

```markdown
# {Idea Name} — Session {n} Report

**Date:** {YYYY-MM-DD}
**Session:** {n}
**Readiness:** {before}% → {after}% (+{delta}%)
**Rounds completed:** {n}
**Ended because:** {reason}
**Agents:** {comma-separated agent names}

---

## Readiness Breakdown

| Dimension | Before | After | Change |
|---|---|---|---|
| Problem statement | x/10 | x/10 | +x |
...

---

## Synthesis

{synthesis from final round meta-agent output}

---

## Open Questions

{numbered list of remaining open questions}

---

## Best Answers Established

{best_answers dict formatted as dimension: answer pairs}

---

## Full Transcript

### Round {n}

#### {Agent Name}
{full message content}

---

#### {Agent Name}
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
