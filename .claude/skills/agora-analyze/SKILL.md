---
name: agora-analyze
description: Analyzes session and specialist performance data from analytics/ to surface trends, improvement signals, and go/no-go validation status. Use when you want to see how the system is performing over time.
version: 1.0.0
argument-hint: "[idea-slug?]"
allowed-tools: Read
---

## Analyze Agora performance data

### Load data

1. Check whether `analytics/sessions.jsonl` and `analytics/specialists.jsonl` exist.
   If neither exists, print:
   ```
   No analytics data yet. Run a debate session first to generate data.
   ```
   and stop.

2. Read `analytics/sessions.jsonl`. Parse each line as a JSON object. Collect all records.
   If a slug argument was provided, filter to records where `slug` matches.

3. Read `analytics/specialists.jsonl`. Parse each line as a JSON object.
   If filtering by slug, filter to records where `session_id` starts with the slug.

### Section 1 — Session trends

4. Print a session trend table, sorted by date ascending:

   ── Session Trends ──────────────────────────────────────────────────────
   Session ID                      Date        Δ Score  KPI Score  Ended
   ──────────────────────────────────────────────────────────────────────
   {slug}-session-{n}-{YYYYMMDD}   YYYY-MM-DD  +NN%     N.NN       {reason}
   ...

   Summary:
   • Sessions analyzed: {count}
   • Average score delta: +{avg}% per session
   • Average KPI score: {avg} ({avg × 100}% of targets met)
   • Most common end reason: {reason}

   KPI score legend: 1.0 = all targets met, 0.5 = all partial, 0.0 = none met

### Section 2 — KPI completion breakdown

5. Across all session records, aggregate the `kpis.dimension_targets` arrays.
   For each dimension, count how many times it appeared as a target and how often it was met/partial/not_met.

   Print:

   ── KPI Completion by Dimension ─────────────────────────────────────────
   Dimension            Targeted  Met    Partial  Not met  Hit rate
   ─────────────────────────────────────────────────────────────────────
   {dimension}          {n}       {n}    {n}      {n}      {pct}%
   ...

   Flag dimensions with hit rate < 40% as: ⚠ consistently missed

6. Across all session records, aggregate `kpis.questions`.
   Count yes/partial/no across all key questions.
   Print:
   • Questions answered (yes): {n} ({pct}%)
   • Questions partially answered: {n} ({pct}%)
   • Questions not addressed: {n} ({pct}%)

### Section 3 — Specialist performance over time

7. Group specialist records by specialist name. For each specialist, sort records by date ascending.

   Print one block per specialist:

   ── {specialist-name} ───────────────────────────────────────────────────
   Date        Version   Adherence  Specificity  Novelty  Resp.  Impact  Overall  Proposal
   ──────────────────────────────────────────────────────────────────────────────────────
   YYYY-MM-DD  v{ver}    {1-5}      {1-5}        {1-5}    {1-5}  {1-5}   {avg}    {yes/no}
   YYYY-MM-DD  v{ver}    ...

   Trend: {improving / stable / declining} — Overall {first} → {last} over {n} sessions

   If a version change is visible between rows, annotate with:
   ↑ v{old} → v{new} (proposal applied)
   and note whether the overall score improved after the version bump.

### Section 4 — Underperforming specialist flags

8. For each specialist with 3 or more session records, compute the average overall score.
   If average < 3.0, flag it:

   ⚠ Underperforming specialists (avg overall < 3.0 over 3+ sessions):
   • {specialist-name}: avg {score} — proposal applied: {yes/no} — consider major revision

   If none, print: ✓ No chronically underperforming specialists detected.

### Section 5 — Improvement loop signal

9. Find any specialists where a version bump occurred between sessions (version field changed).
   For each, compute the delta in overall score before vs. after the bump.

   ── Improvement Loop Signal ─────────────────────────────────────────────
   Specialist           Version bump         Score before  Score after  Delta
   ─────────────────────────────────────────────────────────────────────────
   {specialist-name}    v{old} → v{new}      {score}       {score}      {+/-delta}

   If no version bumps yet:
   Apply a specialist proposal and run another session to generate improvement loop data.

   Threshold: ≥ +0.5 delta for ≥ 1 specialist = improvement loop is working.

### Section 6 — Go/no-go validation status

10. Evaluate each of the 5 go/no-go thresholds and print a status table:

    ── Validation Status ───────────────────────────────────────────────────
    Threshold                                       Status     Detail
    ──────────────────────────────────────────────────────────────────────
    KPI score ≥ 0.60 avg (3+ sessions)              PASS/FAIL  avg: {score}
    Readiness delta ≥ 10% per session (ideas <70%)  PASS/FAIL  avg: {pct}%
    Improvement loop: ≥ +0.5 after proposal         PASS/FAIL  {best delta or "no data"}
    Specialist stability: no avg < 3.0 (3+ sess.)   PASS/FAIL  {worst avg or "ok"}
    Control test                                    PENDING    Run docs/validation/control-test.md

    PASS count: {n}/5

    {If all 4 data-driven pass and control test pending:}
    → Run the control test to complete validation: docs/validation/control-test.md

    {If any data-driven fail:}
    → {specific actionable diagnosis for each failing threshold}

    {If 4/4 data + control test complete:}
    → GO: All thresholds met. The system is validated for productization.
    OR
    → PIVOT: Control test failed. Rethink specialist model before MVP.
