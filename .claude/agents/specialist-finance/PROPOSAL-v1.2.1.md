---
specialist: specialist-finance
current-version: 1.2.0
proposed-version: 1.2.1
change-type: patch
session: ideas/flavor-graph/sessions/flavor-graph-session-1-20260510.md
date: 2026-05-10
status: pending
---

## Proposed Changes to specialist-finance

### Summary
In Round 1 the Finance specialist quoted ~99.8% gross margin without netting Stripe fees, requiring a correction in Round 2. The existing margin calculation instruction only covers session-cap tiers, leaving subscription gross margin computation underspecified.

### Observed Issues

- **[minor]** Gross margin for a flat subscription was quoted as ~99.8% (API cost only) in Round 1. Stripe's 2.9% + $0.30 fee — worth ~9% on a $4.99 charge — was omitted, requiring an explicit correction round later. This wastes a round on a calculation error that should be caught at first mention.
  *Evidence: Round 1 — "Claude Haiku API cost ~$0.002/recipe → ~99.8% gross margin." Corrected in Round 2 to ~88-89%.*

### Proposed Skill Changes

#### Change 1: Extend gross margin instruction to cover subscriptions

**Current instruction:**
```
For every paid tier with a session or usage cap, immediately compute: (monthly price) ÷ (session cap) = revenue per unit, then subtract per-session API/infra cost. If gross margin per unit is below 30%, flag it as broken pricing before endorsing the tier.
```

**Proposed instruction:**
```
For every paid tier, compute gross margin before endorsing it:
- Subscription tiers (no usage cap): gross margin = (price − Stripe fee − avg monthly API cost) / price. Stripe fee = (price × 0.029) + 0.30.
- Usage-capped tiers: (monthly price) ÷ (session cap) = revenue per unit, then subtract per-session API/infra cost.
If gross margin is below 50% on any tier, flag it and propose a fix (raise price or lower cap) before endorsing.
```

**Rationale:** Subscription tiers have a Stripe fee that is material at low price points (9% on $4.99). Requiring the calculation on all tiers prevents the "99.8% margin" error and gives the team accurate numbers from round 1 without needing a correction round.

### Breaking Change Analysis

- **Breaking:** no
- **Affected specialists:** none
- **What breaks:** n/a

### Recommended Testing
In the next session with a subscription-tier product, verify Finance quotes net-of-Stripe margin in round 1 without requiring correction by another specialist.
