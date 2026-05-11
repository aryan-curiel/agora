---
name: agora-write-brainstorm-report
description: Writes a markdown brainstorm session report after a brainstorm completes. Invoked automatically by agora-brainstorm. Not for direct user invocation.
user-invocable: false
version: 1.0.0
---

## Write a brainstorm session report

The caller passes full session data including: slug, session number, date, idea name, dreamer roster, all proposals (with horizon tags and dreamer attribution), skeptic flags and questions (from rounds 2 and 3), and the full transcript.

Create `ideas/{slug}/sessions/{slug}-brainstorm-{n}-{YYYYMMDD}.md` with this structure:

```markdown
# {Idea Name} — Brainstorm Session {n}

**Date:** {YYYY-MM-DD}
**Session:** {n}
**Dreamers:** {comma-separated dreamer names}
**Skeptic grounding:** Yes
**Total proposals generated:** {n}

---

## Quick Wins (0–3 months)

| # | Proposal | Dreamer | Skeptic flagged? |
|---|---|---|---|
| 1 | **{title}**: {1-sentence description} | {dreamer-name} | No |
| 2 | **{title}**: {1-sentence description} | {dreamer-name} | Yes |

---

## Growth Features (3–12 months)

| # | Proposal | Dreamer | Skeptic flagged? |
|---|---|---|---|
| 1 | **{title}**: {1-sentence description} | {dreamer-name} | No |

---

## Moonshots (1+ year)

| # | Proposal | Dreamer | Skeptic flagged? |
|---|---|---|---|
| 1 | **{title}**: {1-sentence description} | {dreamer-name} | No |

---

## Skeptic Flags

{Numbered list of proposals the skeptic flagged as structurally broken, already existing, or based on a false premise. One sentence reason per flag. If none, write "None."}

## Skeptic Questions

1. {question from the skeptic's final round}
2. {question from the skeptic's final round}

---

## Recommendations

Based on this brainstorm session:

- **Strongest quick win to pursue first:** {title} — {1-sentence rationale}
- **Most promising growth feature:** {title} — {1-sentence rationale}
- **Moonshot worth tracking:** {title} — {1-sentence rationale}

---

## Full Transcript

### Round 1

#### The Futurist
{full round 1 output}

---

#### The Builder
{full round 1 output}

---

#### The User Advocate
{full round 1 output}

---

#### The Connector
{full round 1 output}

---

#### The Narrativist
{full round 1 output}

---

### Round 2

#### The Futurist
{full round 2 output}

---

{...repeat for each dreamer...}

---

#### The Skeptic (Grounding)
{skeptic round 2 output}

---

### Round 3

{...repeat pattern...}

---

#### The Skeptic (Grounding)
{skeptic round 3 output}
```

After writing the file, return the filename to the caller.
