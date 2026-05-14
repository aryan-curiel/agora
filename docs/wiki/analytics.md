# Analytics

Agora tracks all session and agent performance in append-only JSONL files. Each line is a standalone JSON object. Files are created on first write and never overwritten.

---

## Files Overview

| File | Written by | One record per | Purpose |
|---|---|---|---|
| `analytics/sessions.jsonl` | `agora-run-debate` | Debate session | Session outcomes, score deltas, KPI results |
| `analytics/specialists.jsonl` | `agora-review-specialists` | Specialist × session | Per-specialist performance scores and proposals |
| `analytics/brainstorms.jsonl` | `agora-brainstorm` | Brainstorm session | Proposal counts by horizon, dreamer versions |
| `analytics/dreamers.jsonl` | `agora-brainstorm` | Dreamer × brainstorm session | Per-dreamer quality scores |

---

## `analytics/sessions.jsonl`

One JSON record per completed debate session.

```json
{
  "session_id": "flavour-graph-session-3-20260511",
  "slug": "flavour-graph",
  "idea_name": "Flavour Graph",
  "date": "2026-05-11",
  "rounds": 2,
  "score_before": 79,
  "score_after": 85,
  "delta": 6,
  "ended_reason": "target_reached",
  "kpi_score": 0.7,
  "kpis": {
    "dimension_targets": [
      {
        "dimension": "target_user",
        "before": 7,
        "target": 9,
        "after": 9,
        "result": "met"
      },
      {
        "dimension": "go_to_market",
        "before": 7,
        "target": 9,
        "after": 9,
        "result": "met"
      },
      {
        "dimension": "problem_statement",
        "before": 8,
        "target": 10,
        "after": 9,
        "result": "partial"
      }
    ],
    "questions": [
      {
        "question": "Has the founder confirmed inspiration fatigue as the single JTBD?",
        "answered": "partial"
      },
      {
        "question": "Has anyone matching the annotator ICP been interviewed yet?",
        "answered": "partial"
      }
    ]
  },
  "specialists": [
    "specialist-skeptic",
    "specialist-market-analyst",
    "specialist-product-manager",
    "specialist-growth"
  ],
  "specialist_versions": {
    "specialist-skeptic": "1.1.1",
    "specialist-market-analyst": "1.1.0",
    "specialist-product-manager": "1.1.0",
    "specialist-growth": "1.1.1"
  }
}
```

### Field Reference

| Field | Type | Description |
|---|---|---|
| `session_id` | string | `{slug}-session-{n}-{YYYYMMDD}` — unique identifier |
| `slug` | string | Idea slug |
| `idea_name` | string | Human-readable idea name |
| `date` | string | ISO date `YYYY-MM-DD` |
| `rounds` | integer | How many rounds actually ran |
| `score_before` | integer | Readiness % at session start |
| `score_after` | integer | Readiness % at session end |
| `delta` | integer | `score_after - score_before` |
| `ended_reason` | string | `"max_rounds"` or `"target_reached"` |
| `kpi_score` | float | 0.0–1.0 — fraction of KPIs met or partially met |
| `kpis.dimension_targets` | array | Per-dimension: before, target, after, result |
| `kpis.questions` | array | Per-question: text, answered (yes/partial/no) |
| `specialists` | array | Specialist names in roster order |
| `specialist_versions` | object | `{name: version}` — version of each specialist at time of session |

### `kpis.dimension_targets[].result` values

| Value | Condition |
|---|---|
| `"met"` | `after >= target` |
| `"partial"` | `after > before AND after < target` |
| `"not_met"` | `after <= before` |

### `kpis.questions[].answered` values

| Value | Condition |
|---|---|
| `"yes"` | Clear, specific answer was established in the transcript |
| `"partial"` | Progress was made but no definitive answer |
| `"no"` | Not addressed |

---

## `analytics/specialists.jsonl`

One JSON record per specialist per session review. Written by `agora-review-specialists`.

```json
{
  "session_id": "flavour-graph-session-3-20260511",
  "date": "2026-05-11",
  "specialist": "specialist-market-analyst",
  "version": "1.1.0",
  "scores": {
    "adherence": 4,
    "specificity": 5,
    "novelty": 4,
    "responsiveness": 3,
    "impact": 4
  },
  "word_count_compliance": true,
  "overall": 4.0,
  "severity": "minor",
  "proposal_written": true,
  "proposal_file": ".claude/agents/specialist-market-analyst/PROPOSAL-v1.1.1.md"
}
```

### Field Reference

| Field | Type | Description |
|---|---|---|
| `session_id` | string | Links back to sessions.jsonl record |
| `date` | string | ISO date of the review |
| `specialist` | string | Agent name |
| `version` | string | Agent version at time of session |
| `scores.adherence` | int 1–5 | Followed stated role and output structure |
| `scores.specificity` | int 1–5 | Named real technologies, numbers, companies |
| `scores.novelty` | int 1–5 | Introduced new info each round, not repetition |
| `scores.responsiveness` | int 1–5 | Acknowledged and built on other specialists |
| `scores.impact` | int 1–5 | Contributions measurably raised dimension scores |
| `word_count_compliance` | boolean | Stayed within 250–400 word limit |
| `overall` | float | Mean of 5 scores, rounded to 1 decimal |
| `severity` | string | `none` / `minor` / `moderate` / `major` |
| `proposal_written` | boolean | Whether a PROPOSAL file was generated |
| `proposal_file` | string/null | Path to proposal file, or null |

### Score Rubric (1–5)

| Score | Meaning |
|---|---|
| 1 | Did not meet the criterion at all |
| 2 | Attempted but mostly failed |
| 3 | Partially met — some instances of compliance |
| 4 | Mostly met — minor gaps |
| 5 | Fully met — exemplary performance |

---

## `analytics/brainstorms.jsonl`

One JSON record per completed brainstorm session. Written by `agora-brainstorm`.

```json
{
  "session_id": "agora-saas-brainstorm-1-20260512",
  "slug": "agora-saas",
  "idea_name": "Agora SaaS",
  "date": "2026-05-12",
  "rounds": 3,
  "proposals_generated": 61,
  "proposals_by_horizon": {
    "quick_win": 26,
    "growth_feature": 19,
    "moonshot": 16
  },
  "flagged_proposals": 4,
  "dreamers": [
    "dreamer-futurist",
    "dreamer-builder",
    "dreamer-user-advocate",
    "dreamer-connector",
    "dreamer-narrativist"
  ],
  "dreamer_versions": {
    "dreamer-futurist": "1.0.0",
    "dreamer-builder": "1.0.0",
    "dreamer-user-advocate": "1.0.0",
    "dreamer-connector": "1.0.0",
    "dreamer-narrativist": "1.0.0"
  }
}
```

### Field Reference

| Field | Type | Description |
|---|---|---|
| `session_id` | string | `{slug}-brainstorm-{n}-{YYYYMMDD}` |
| `slug` | string | Idea slug |
| `idea_name` | string | Human-readable idea name |
| `date` | string | ISO date |
| `rounds` | integer | Always 3 for brainstorms |
| `proposals_generated` | integer | Total proposals across all dreamers and rounds |
| `proposals_by_horizon.quick_win` | integer | Count of quick-win proposals |
| `proposals_by_horizon.growth_feature` | integer | Count of growth-feature proposals |
| `proposals_by_horizon.moonshot` | integer | Count of moonshot proposals |
| `flagged_proposals` | integer | Count of proposals flagged by the Skeptic |
| `dreamers` | array | Always all 5 dreamer names |
| `dreamer_versions` | object | Version of each dreamer at time of session |

---

## `analytics/dreamers.jsonl`

One JSON record per dreamer per brainstorm session. Written by `agora-brainstorm`.

```json
{
  "session_id": "agora-saas-brainstorm-1-20260512",
  "date": "2026-05-12",
  "dreamer": "dreamer-futurist",
  "version": "1.0.0",
  "scores": {
    "originality": 4,
    "specificity": 5,
    "cross_pollination": 3,
    "horizon_adherence": 5
  },
  "word_count_compliance": true,
  "proposals_count": 8,
  "flagged_count": 1,
  "overall": 4.25,
  "proposal_written": false,
  "proposal_file": null
}
```

### Field Reference

| Field | Type | Description |
|---|---|---|
| `session_id` | string | Links to brainstorms.jsonl record |
| `date` | string | ISO date |
| `dreamer` | string | Agent name |
| `version` | string | Agent version at time of session |
| `scores.originality` | int 1–5 | Proposed directions not already obvious |
| `scores.specificity` | int 1–5 | Concrete mechanisms, timeframes, technologies — not vague |
| `scores.cross_pollination` | int 1–5 | Explicitly built on / forked another dreamer's proposals in Round 2+ |
| `scores.horizon_adherence` | int 1–5 | Followed horizon assignment (round 1 open; rounds 2–3 directed) |
| `word_count_compliance` | boolean | Stayed within 250–400 words |
| `proposals_count` | integer | Total proposals generated across all rounds |
| `flagged_count` | integer | Proposals flagged by the Skeptic |
| `overall` | float | Mean of 4 scores, rounded to 2 decimal places |
| `proposal_written` | boolean | Whether an improvement proposal was written (via agora-review-specialists) |
| `proposal_file` | string/null | Path to proposal file, or null |

---

## Analytics Dashboard

A Streamlit dashboard (`analytics/dashboard.py`) reads all JSONL files and displays:

- Session score deltas over time
- Specialist performance trends by version
- Readiness distribution across ideas
- KPI achievement rates
- Dreamer proposal counts and quality scores

**Dependencies:** `pandas`, `plotly`, `streamlit` (see `analytics/pyproject.toml`)

Run: `cd analytics && streamlit run dashboard.py`

---

## Querying the Analytics

Since records are JSONL (one JSON object per line), they can be queried with standard tools:

```bash
# Average score delta across all sessions
jq '.delta' analytics/sessions.jsonl | awk '{sum+=$1; count++} END {print sum/count}'

# Sessions that ended by reaching the target
jq 'select(.ended_reason == "target_reached")' analytics/sessions.jsonl

# Specialists with average overall score < 3.5
jq 'select(.overall < 3.5) | {specialist, overall, severity}' analytics/specialists.jsonl

# Total proposals generated by horizon
jq '[.proposals_by_horizon.quick_win, .proposals_by_horizon.growth_feature, .proposals_by_horizon.moonshot]' analytics/brainstorms.jsonl
```
