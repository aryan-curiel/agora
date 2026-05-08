---
agent: specialist-skeptic
current-version: 1.1.0
proposed-version: 1.1.1
change-type: patch
session: ideas/agora/sessions/agora-session-1-20260508.md
date: 2026-05-08
status: pending
---

## Proposed Changes to specialist-skeptic

### Summary
The Skeptic stopped ending responses with explicitly formulated questions in Rounds 2 and 3, instead closing with declarative statements. The fix clarifies that the two-question requirement is a hard structural rule that applies every round without exception.

### Observed Issues

- **[moderate]** In Rounds 2 and 3, the agent closed with statements rather than questions, violating the explicit instruction "End with exactly 2 sharp questions the team must answer before this idea can move forward."
  *Evidence: Round 2 — "All specialists run on same underlying model — legitimacy risk when sophisticated users notice." (declarative statement, not a question)*
  *Evidence: Round 3 — "Founders must trust AI disagreement as legitimate signal; if debate feels like theater, value proposition collapses." (declarative statement, not a question)*

### Proposed Skill Changes

#### Change 1: Enforce 2-question closing in every round

**Current instruction:**
```
End with exactly 2 sharp questions the team must answer before this idea can move forward.
```

**Proposed instruction:**
```
End with exactly 2 sharp questions the team must answer before this idea can move forward. Both must be phrased as explicit questions (ending with "?"), must not repeat questions from prior rounds, and this requirement applies every round without exception — not just the first.
```

**Rationale:** The current phrasing is clear, but the agent treated it as optional in later rounds, defaulting to statements when raising new risks. Making "every round without exception" explicit prevents this drift and ensures agora-meta-specialist and session reports consistently receive the two-question signal to surface in synthesis.

### Breaking Change Analysis

- **Breaking:** no
- **Affected agents:** none
- **What breaks:** n/a

### Recommended Testing
In the next session, verify that every Skeptic response (including rounds 2+) ends with exactly 2 lines containing "?" characters.
