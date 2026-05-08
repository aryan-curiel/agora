---
agent: agent-finance
current-version: 1.1.0
proposed-version: 1.2.0
change-type: minor
session: ideas/agora/sessions/agora-session-1-20260508.md
date: 2026-05-08
status: pending
---

## Proposed Changes to agent-finance

### Summary
Finance proposed a $12/month, 10-session tier in Round 1 while simultaneously stating the per-session API cost was $0.40–$1.20 — but did not cross-check the two figures to catch the near-zero gross margin. The margin problem took until Round 3 to surface and fix. The fix adds an explicit per-unit margin check to the pricing proposal step.

### Observed Issues

- **[minor]** Finance proposed a $12/month tier with 10 sessions/month without computing per-unit economics against the API cost estimate given in the same response. $12 ÷ 10 = $1.20 revenue per session vs. $1.20 API cost = ~0% gross margin. This required two additional rounds of iteration to identify and fix.
  *Evidence: Round 1 — "Solo: $12/month (unlimited ideas, 10 sessions/month)" and "PoC already done, ~$0–50 API costs, $0.40–$1.20 per session" — both figures present but not cross-checked.*
  *Evidence: Round 3 — "Solo tier margin math: $12/8 sessions = $9.60 API cost → ~$2.40 gross margin = 20%. Fix: 5 sessions or raise to $19/mo." — caught and fixed here, two rounds late.*

### Proposed Skill Changes

#### Change 1: Add per-unit margin check to pricing proposal step

**Current instruction:**
```
Otherwise, propose 1-2 specific monetization models with rough pricing. Not "freemium" — "free tier up to 3 projects, $12/month for unlimited, $49/month for teams."
```

**Proposed instruction:**
```
Otherwise, propose 1-2 specific monetization models with rough pricing. Not "freemium" — "free tier up to 3 projects, $12/month for unlimited, $49/month for teams." For every paid tier with a session or usage cap, immediately compute: (monthly price) ÷ (session cap) = revenue per unit, then subtract per-session API/infra cost. If gross margin per unit is below 30%, flag it as broken pricing before endorsing the tier.
```

**Rationale:** Finance already estimates per-session API cost as part of the budget step, so the data is always available. Making the cross-check explicit prevents the agent from proposing pricing tiers it has not validated, which forces correction rounds that consume session token budget.

### Breaking Change Analysis

- **Breaking:** no
- **Affected agents:** none
- **What breaks:** n/a

### Recommended Testing
In the next session with a SaaS or subscription pricing model, verify that Finance's Round 1 response includes an explicit per-tier margin calculation before endorsing any session-capped tier.
