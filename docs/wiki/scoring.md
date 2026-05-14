# Scoring System

Agora tracks idea readiness across 10 dimensions. Each dimension is scored 0–10 per round by the `agora-score-round` sub-skill. The overall readiness percentage is the mean across all scored dimensions.

---

## The 10 Readiness Dimensions

| # | Key | Question it answers | Score = 10 when... |
|---|---|---|---|
| 1 | `problem_statement` | Is the problem clearly defined? | The problem is specific, the affected user is named, the current cost of the problem is quantified |
| 2 | `target_user` | Is the target persona specific? | The ICP is named (not a category), recruitment channels are specified, a JTBD is stated |
| 3 | `core_features` | Is the MVP feature set scoped? | Features are enumerated, explicitly cut features are listed, a "moment of value" is defined |
| 4 | `tech_stack` | Has the technology approach been decided? | Named frameworks, databases, APIs, hosting — not "React or Vue" but "React + Vite + SQLite + Fly.io" |
| 5 | `go_to_market` | Is there a concrete first distribution plan? | Week-by-week plan for first 4 weeks, specific channel named, first 100 users path described |
| 6 | `key_risks` | Have main risks been identified and addressed? | Top 3 risks named with mitigation strategies or explicit monitoring plans |
| 7 | `poc_scope` | Is the minimum provable concept defined? | A binary pass/fail gate is defined, the PoC is buildable in 1–2 weekends, success condition stated |
| 8 | `success_metrics` | Are measurable success criteria defined? | Metrics have numbers (not "increase engagement"), time-bound, and tied to the PoC gate |
| 9 | `monetization` | Is there a revenue model? | Specific model named (freemium/$X/mo, per-seat, usage-based), gross margin estimated, pricing defended |
| 10 | `budget_estimates` | Are rough cost/effort estimates available? | Per-phase breakdown: PoC / MVP / V1 with both time (dev-weeks) and dollar costs |

**N/A rule:** If `monetization` is N/A (personal project or OSS), it is excluded from the mean. The percentage is then calculated from the remaining 9 dimensions.

---

## Scoring Rubric (0–10 per dimension)

| Score | Meaning |
|---|---|
| 0 | Not addressed at all |
| 1–2 | Briefly mentioned, no specifics |
| 3–4 | Direction established but vague — lacks concrete details |
| 5–6 | Partially developed — some specifics but key gaps remain |
| 7–8 | Well-developed — specific and actionable, minor gaps acceptable |
| 9–10 | Complete — all key questions answered, specific, defensible |

---

## Readiness Percentage

```
readiness_percentage = round(mean(dimension_scores) / 10 * 100)
```

Where the mean excludes any N/A dimensions.

### Readiness Tiers

| Range | Tier | Meaning |
|---|---|---|
| 0–29% | New idea | Max 3 debate rounds; needs foundational work on most dimensions |
| 30–84% | In development | Max 2 debate rounds per session; some dimensions are strong |
| 85%+ | Ready | Session ends — idea is fully planned and ready to build |

---

## Session KPI Framework

Before every debate session, `agora-run-debate` defines measurable goals:

### Dimension Targets

Select the **3 lowest-scoring dimensions** from the current breakdown. For each:

```
target = min(current_score + 2, 10)
```

If current score is 0, target is 2.

Example:
```
Dimension targets:
• go_to_market:      0/10 → 2/10
• poc_scope:         0/10 → 2/10
• success_metrics:   0/10 → 2/10
```

### Key Questions

Select the **2 most critical open questions** from the idea's `## Open Questions` list. If fewer than 2 exist, use what is available.

### KPI Score Calculation

After the session, each KPI is evaluated:

| Dimension target | Result | Points |
|---|---|---|
| final_score ≥ target | Met | 1.0 |
| final_score > before AND < target | Partial | 0.5 |
| final_score ≤ before | Not met | 0 |

| Question | Result | Points |
|---|---|---|
| Clear, specific answer established | Yes | 1.0 |
| Progress made but no definitive answer | Partial | 0.5 |
| Not addressed | No | 0 |

```
kpi_score = (sum of points) / (total KPI count)
```

Range: 0.0–1.0. Recorded in `analytics/sessions.jsonl`.

---

## agora-score-round Output

The `agora-score-round` sub-skill acts as a meta-specialist. It reads all specialist contributions from the round and outputs a structured JSON object:

```json
{
  "scores": {
    "problem_statement": 7,
    "target_user": 6,
    "core_features": 5,
    "tech_stack": 8,
    "go_to_market": 3,
    "key_risks": 5,
    "poc_scope": 4,
    "success_metrics": 3,
    "monetization": 2,
    "budget_estimates": 1
  },
  "readiness_percentage": 47,
  "synthesis": "This round established a specific ICP (Flavour Thesaurus owners), a concrete tech stack (React/Vite + FastAPI + SQLite + Fly.io), and a first distribution channel (r/cookbooks). Key remaining gaps are monetization model and PoC success gate.",
  "open_questions": [
    "What is the single JTBD — inspiration fatigue, flavour education, or recipe discovery?",
    "Has a Bloomsbury licensing inquiry been initiated?",
    "What is the freemium vs. paid split for the MVP?"
  ],
  "best_answers": {
    "problem_statement": "Home cooks who own The Flavour Thesaurus experience inspiration fatigue when choosing what to cook — they have flavour knowledge but can't quickly explore combinations.",
    "tech_stack": "React/Vite frontend, FastAPI backend, SQLite for the flavour graph, Fly.io for hosting, Anthropic SDK for recipe generation."
  }
}
```

The `synthesis` field is the most important output — it replaces the full idea description in specialist prompts for all subsequent rounds, compressing context while preserving essential information.

---

## Score Progression Example

From the Flavour Graph idea (3 sessions):

```
Session 1 (3 rounds): 16% → 69%  (+53%)  — foundational dimensions established
Session 2 (2 rounds): 69% → 79%  (+10%)  — tech stack and budget refined
Session 3 (2 rounds): 79% → 85%  (+6%)   — target_reached: session ended early
```

Individual dimension progression (Session 1, flavour-graph):

| Dimension | Start | After R1 | After R2 | After R3 |
|---|---|---|---|---|
| problem_statement | 0 | 4 | 5 | 6 |
| target_user | 0 | 4 | 6 | 7 |
| core_features | 3 | 5 | 6 | 7 |
| tech_stack | 1 | 3 | 5 | 6 |
| go_to_market | 0 | 3 | 5 | 7 |
| key_risks | 2 | 4 | 5 | 5 |
| poc_scope | 0 | 3 | 4 | 5 |
| success_metrics | 0 | 2 | 3 | 4 |
| monetization | 0 | 2 | 3 | 4 |
| budget_estimates | 0 | 2 | 3 | 5 |

---

## Milestone Update Format

Printed after every round during a debate session:

```
── Round 1 complete ────────────────────────────
Readiness: 16% → 44%

This round established a specific ICP and a concrete tech stack...

Dimension progress:
  problem_statement  ████████░░  6/10  (+6)
  target_user        ███████░░░  7/10  (+7)
  core_features      █████░░░░░  5/10  (+5)
  tech_stack         ███░░░░░░░  3/10  (+3)
  go_to_market       ███░░░░░░░  3/10  (+3)
  key_risks          ████░░░░░░  4/10  (+4)
  poc_scope          ███░░░░░░░  3/10  (+3)
  success_metrics    ██░░░░░░░░  2/10  (+2)
  monetization       ██░░░░░░░░  2/10  (+2)
  budget_estimates   ██░░░░░░░░  2/10  (+2)

Open questions remaining:
• What is the single JTBD?
• Has Bloomsbury licensing been checked?
• What is the PoC success gate?
```
