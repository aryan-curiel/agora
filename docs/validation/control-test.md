# Control Test Protocol — Agora vs. Single-Prompt Claude

## Purpose

Validate that multi-agent debate produces structurally better planning outputs than a single well-crafted Claude prompt. This is the most important validation gate before productizing Agora. If single-prompt Claude ties or wins, the multi-agent structure adds noise, not signal.

## When to run

After at least 2 Agora sessions have been completed and the KPI score threshold is passing (≥ 0.60 average). Do not run the control test before the system has had a chance to operate at its current best.

## Setup

### Ideas to test

Pick **5 ideas you have not previously run through Agora**. They should be:
- Real startup or project ideas (not toy examples)
- At different stages — some half-formed, some more developed
- Not Agora itself (avoid evaluation bias from familiarity)

Record them here before starting:

| # | Idea name | One-line description |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

### Blind rating

The same person rates both outputs. To reduce recall bias:
1. Run all 5 single-prompt outputs first and save them.
2. Run all 5 Agora sessions next and save the session reports.
3. Wait at least 24 hours.
4. Rate all 10 outputs without referring back to which method produced which — label them only as A or B and record the mapping separately.

---

## Single-prompt procedure (Method A)

For each idea, use exactly this prompt, replacing only the `[IDEA]` section:

```
You are a brutal but constructive startup advisor. Analyze this idea across 10 dimensions:
problem_statement, target_user, core_features, tech_stack, go_to_market, key_risks, poc_scope,
success_metrics, monetization, budget_estimates.

For each dimension: score it 1-10, explain the score in 2-3 sentences, and name the single most
important thing that must be resolved before moving forward.

Then provide: a prioritized list of the 5 most critical open questions, a concrete PoC scope
(what is the minimum thing you can build to validate the core assumption), and 3 specific risks
with mitigations.

Be specific. Name real technologies, real competitors, real distribution channels, real numbers.
Vague advice is worthless.

IDEA: [paste the idea description here]
```

Save the full response as `docs/validation/control-test-results/idea-{n}-method-A.md`.

---

## Agora procedure (Method B)

For each idea:
1. Run `/agora-add-idea` to add the idea to the system
2. Run `/agora-run-debate [slug]` — let it complete all 3 rounds
3. Save the session report from `ideas/{slug}/sessions/` as `docs/validation/control-test-results/idea-{n}-method-B.md`

Do not run `agora-review-specialists` between ideas — you want consistent specialist behavior across all 5 tests.

---

## Scoring rubric

Rate each output on 5 criteria, 1–5 each. Score both A and B before looking at the mapping.

| Criterion | 1 | 3 | 5 |
|---|---|---|---|
| **Specificity** | Vague generalities, no real names | Some specifics, some generic | Real technologies, companies, numbers, channels named throughout |
| **Novelty** | Says what you already know | Mostly expected, one surprise | Multiple non-obvious insights you would not have generated alone |
| **Actionability** | Cannot act on this output | Some actionable steps, some not | Clear next actions with enough detail to start tomorrow |
| **Risk coverage** | Risks are obvious or missing | Identifies main risks, weak mitigations | Identifies non-obvious risks with specific, credible mitigations |
| **Structure** | Hard to navigate, key info buried | Organized but some gaps | All 10 dimensions addressed, easy to scan, priorities clear |

---

## Results table

Fill this in after rating. Use the A/B mapping you set aside.

### Idea 1: [name]

| Criterion | Method A (single prompt) | Method B (Agora) | Winner |
|---|---|---|---|
| Specificity | /5 | /5 | A / B / Tie |
| Novelty | /5 | /5 | A / B / Tie |
| Actionability | /5 | /5 | A / B / Tie |
| Risk coverage | /5 | /5 | A / B / Tie |
| Structure | /5 | /5 | A / B / Tie |
| **Total** | **/25** | **/25** | |
| **Criteria won** | | | Agora wins {n}/5 |

### Idea 2: [name]

| Criterion | Method A | Method B | Winner |
|---|---|---|---|
| Specificity | /5 | /5 | |
| Novelty | /5 | /5 | |
| Actionability | /5 | /5 | |
| Risk coverage | /5 | /5 | |
| Structure | /5 | /5 | |
| **Total** | **/25** | **/25** | Agora wins {n}/5 |

### Idea 3: [name]

| Criterion | Method A | Method B | Winner |
|---|---|---|---|
| Specificity | /5 | /5 | |
| Novelty | /5 | /5 | |
| Actionability | /5 | /5 | |
| Risk coverage | /5 | /5 | |
| Structure | /5 | /5 | |
| **Total** | **/25** | **/25** | Agora wins {n}/5 |

### Idea 4: [name]

| Criterion | Method A | Method B | Winner |
|---|---|---|---|
| Specificity | /5 | /5 | |
| Novelty | /5 | /5 | |
| Actionability | /5 | /5 | |
| Risk coverage | /5 | /5 | |
| Structure | /5 | /5 | |
| **Total** | **/25** | **/25** | Agora wins {n}/5 |

### Idea 5: [name]

| Criterion | Method A | Method B | Winner |
|---|---|---|---|
| Specificity | /5 | /5 | |
| Novelty | /5 | /5 | |
| Actionability | /5 | /5 | |
| Risk coverage | /5 | /5 | |
| Structure | /5 | /5 | |
| **Total** | **/25** | **/25** | Agora wins {n}/5 |

---

## Summary

| Idea | Agora criteria won | Pass (≥ 4/5)? |
|---|---|---|
| 1 | /5 | |
| 2 | /5 | |
| 3 | /5 | |
| 4 | /5 | |
| 5 | /5 | |
| **Ideas where Agora wins ≥ 4/5 criteria** | **/5** | |

---

## Decision

**Pass threshold:** Agora wins ≥ 4/5 criteria for ≥ 3/5 ideas.

| Result | Interpretation | Action |
|---|---|---|
| ≥ 3 ideas pass | Multi-agent debate adds clear value | **GO** — proceed to hosted MVP |
| Exactly 2 ideas pass | Mixed signal | Investigate which criteria Agora loses on — likely specificity or novelty. Improve those specialist skills before re-running. |
| ≤ 1 idea passes | Single prompt is competitive | **PIVOT** — the specialist model is not working. Consider: fewer specialists, different role definitions, or a different output format. Do not productize in current form. |

**Date run:** ___________
**Decision:** ___________
**Notes:**
