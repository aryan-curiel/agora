---
specialist: specialist-skeptic
current-version: 1.1.1
proposed-version: 1.1.2
change-type: patch
session: ideas/flavour-graph/sessions/flavour-graph-session-2-20260511.md
date: 2026-05-11
status: applied
applied-date: 2026-05-11
---

## Proposed Changes to specialist-skeptic

### Summary
The two-question close from v1.1.1 partially recurred in session 2: Round 1's first question was phrased as a decision prompt ending in "." rather than "?", and Round 2 had no question close at all. The fix adds a structural output rule requiring the response to end with a labelled "Questions:" block.

### Observed Issues

- **[minor]** Round 1 question 1 ("Which single JTBD? (Inspiration fatigue — proposed.)") ends in "." after a parenthetical, not "?" — does not satisfy the explicit-question requirement.
  *Evidence: Round 1 close — "1. Which single JTBD? (Inspiration fatigue — proposed.)" — trailing character is "." not "?"*

- **[minor]** Round 2 response contains no 2-question close at all. The analysis described the parity test concern and path B recommendation but did not surface them as explicit questions for the team to answer.
  *Evidence: Round 2 ends with "THAT test is defensible." — a declarative statement, not 2 questions.*

### Proposed Skill Changes

#### Change 1: Require a labelled "Questions:" block as the final section

**Current instruction:**
```
End with exactly 2 sharp questions the team must answer before this idea can move forward. Both must be phrased as explicit questions (ending with "?"), must not repeat questions from prior rounds, and this requirement applies every round without exception — not just the first.
```

**Proposed instruction:**
```
End with exactly 2 sharp questions the team must answer before this idea can move forward. Format them as the final section of your response, labelled exactly:

Questions:
1. {question ending with "?"}
2. {question ending with "?"}

Both must end with "?". Do not add parenthetical clarifications after the "?" — the question mark must be the last character of each line. Do not repeat questions from prior rounds. This block is mandatory every round without exception.
```

**Rationale:** The existing instruction is clear about the content requirement but not the format. The parenthetical pattern ("Which JTBD? (Inspiration fatigue — proposed.)") allows the agent to bury the "?" mid-sentence and terminate with a different character. Making the block structure explicit — with "?" as the terminal character, no trailing text — closes this loophole and makes compliance mechanically verifiable.

### Breaking Change Analysis

- **Breaking:** no
- **Affected specialists:** none
- **What breaks:** n/a

### Recommended Testing
In the next session, verify that every Skeptic response ends with a "Questions:" section containing exactly 2 lines, each ending with "?" as the final character, with no trailing parentheticals or periods.
