---
agent: specialist-growth
current-version: 1.1.0
proposed-version: 1.1.1
change-type: patch
session: ideas/agora/sessions/agora-session-1-20260508.md
date: 2026-05-08
status: pending
---

## Proposed Changes to specialist-growth

### Summary
In Round 2, Growth referenced "5 newsletter writers" without naming any of them, violating the explicit instruction to name specific people, publications, and communities. The fix tightens the naming rule to cover every item mentioned in the response, not just the primary channel.

### Observed Issues

- **[minor]** In Round 2, Growth's week-by-week plan referenced "outreach to 5 newsletter writers" without naming a single one — despite Round 1 correctly naming TLDR AI and Ben's Bites, and Round 3 correctly naming Rohan Chaubey and KP. The agent can apply the rule but drops it when under space pressure.
  *Evidence: Round 2 — "W2: IH Show IH + outreach to 5 newsletter writers" — no names given for any of the five.*

### Proposed Skill Changes

#### Change 1: Tighten naming rule to cover every item mentioned

**Current instruction:**
```
Name specific subreddits, newsletters, communities, influencers, or events.
```

**Proposed instruction:**
```
Name specific subreddits, newsletters, communities, influencers, or events. This applies to every item you mention — do not write "5 newsletter writers" or "a few Discord communities" without naming them. If you cannot name it, drop it from the response entirely.
```

**Rationale:** The agent already knows how to apply this rule (it did so in Rounds 1 and 3) but reverts to vague placeholders when adding secondary items in later rounds. Making "if you cannot name it, drop it" explicit removes the temptation to include unvalidated references.

### Breaking Change Analysis

- **Breaking:** no
- **Affected agents:** none
- **What breaks:** n/a

### Recommended Testing
In the next session, verify that every person, newsletter, or community mentioned in any Growth round response has a specific name attached.
