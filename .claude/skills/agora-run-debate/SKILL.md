---
name: agora-run-debate
description: Run a full multi-agent debate session to develop an idea. Use when the user wants to debate, develop, work on, or improve an idea. This is the core workflow of Agora.
disable-model-invocation: true
argument-hint: "[idea-id]"
allowed-tools: Read Write Agent
version: 1.3.0
author: Aryan Curiel
---

## Run a debate session

### Setup

1. Resolve the idea from $ARGUMENTS. If empty, read ideas_index.md and ask the user to pick from active ideas.
2. Read ideas/{slug}/README.md fully. Note current readiness score and breakdown.
   Also extract the `## Constraints` section if present. Format it as a flat list:
   - {constraint} (Rationale: {rationale})
   Store as [CONSTRAINTS]. If the section is absent or has no rows, set [CONSTRAINTS] to null.
3. Determine session number: count existing rows in the idea's Session History table + 1.
4. Read .claude/skills/agora-lead-specialist/SKILL.md to understand how to invoke the lead agent.

### Establish session KPIs

5. Before invoking any specialists, define measurable goals for this session:

   a. From the current readiness breakdown, select the 3 lowest-scoring dimensions.
      For each, compute a target score: min(current_score + 2, 10). If current is 0, target is 2.

   b. From the idea's Open Questions list (in ideas/{slug}/README.md), select the 2 most critical
      unanswered questions. If fewer than 2 exist, use what is available.

   c. Save these as [SESSION_KPIS]:
      ```
      dimension_targets: [{dimension, before, target}, ...]
      questions: [{text}, ...]
      ```

   d. Print the session KPIs before the first round:

      ── Session KPIs ───────────────────────────────
      Readiness target: {current}% → {estimated target based on dimension gains}%

      Dimension targets:
      • {dimension}: {current}/10 → {target}/10
      • {dimension}: {current}/10 → {target}/10
      • {dimension}: {current}/10 → {target}/10

      Key questions to answer:
      • {question 1}
      • {question 2}
      ───────────────────────────────────────────────

### Invoke the lead agent

6. Invoke /agora-lead-specialist with the idea slug as argument.
   If [CONSTRAINTS] is not null, include it in the context so the lead specialist can factor constraints into roster selection.
   The lead agent returns a JSON array of specialist skill names to include this session.
   Example: ["specialist-skeptic", "specialist-tech-lead", "specialist-market-analyst", "specialist-finance"]
   Save this as the roster for this session.

### Run debate rounds

Read CLAUDE.md for session defaults. Set max rounds adaptively:
- If current readiness score ≥ 30% → use `max_rounds_partial` (default: 2)
- Otherwise → use `max_rounds` (default: 3)

Check for `## Session overrides` in CLAUDE.md and apply any matching keys.

For each round:

7. Print a round header: "── Round {n} of {max} ──────────────────────"

8. For each specialist in the roster — invoke them ONE AT A TIME, sequentially.
   Do NOT issue multiple specialist Agent calls in the same message. Each specialist
   must see the prior specialists' responses from this round before contributing.

   For each specialist {name}:
   a. Read .claude/skills/{name}/MEMORY.md if it exists. Save content as [MEMORY].
      If the file does not exist, [MEMORY] is empty — omit [YOUR MEMORY] from the prompt.
   b. Call the Agent tool (foreground — wait for this response before issuing the next):
      - subagent_type: "{name}"  (e.g. "specialist-finance")
      - description: "{Specialist display name} — Round {n}"
      - prompt:

        [YOUR MEMORY]
        {[MEMORY] — omit this block entirely if MEMORY.md did not exist}

        [CONSTRAINTS]
        {formatted constraint list if not null; omit this section if null}

        [IDEA]
        {Round 1: idea name + full description + current readiness breakdown (scores only)}
        {Round 2+: idea name only + [ROUND_SYNTHESIS] from the previous round's agora-score-round output}

        [PRIOR ROUND MESSAGES] (last 10 max across all previous rounds)
        {all specialist messages from prior rounds, each labeled "SpecialistName: ..."}

        [THIS ROUND SO FAR]
        {all specialist responses collected so far this round, each labeled "SpecialistName: ..."}
        {If this is the first specialist this round: "None — you are first this round."}

        Build on what others said. Focus on what has NOT been addressed yet.

   c. After the Agent call returns, print the response in a panel:
      ┌─ {Specialist Name} ─────────────────────────────┐
      │ {response}                                       │
      └──────────────────────────────────────────────────┘
   d. Append the response to the round message list, labeled "{Specialist Name}:".

9. After all specialists in the round have responded, invoke /agora-score-round with:
   - The idea slug
   - All messages from this round
   - Current scores from the idea file
   - [CONSTRAINTS]: {formatted constraint list from step 2, if not null}

10. /agora-score-round returns updated scores and synthesis. Print a milestone update:

    ── Round {n} complete ──────────────────────────
    Readiness: {old}% → {new}%

    {synthesis paragraph}

    Dimension progress:
    {updated breakdown table with █░ bars}

    Open questions remaining:
    • {question 1}
    • {question 2}
    • {question 3}

11. Update ideas/{slug}/README.md with new scores, open questions, and best answers.

12. Check termination:
    - If rounds completed = max rounds → end, reason: "max_rounds"
    - If readiness >= 85% → end, reason: "target_reached"
    - Otherwise continue to next round.

### Finish

13. Invoke /agora-write-report with the session data AND [SESSION_KPIS] so the report includes the KPI section.
14. Update the Session History table in ideas/{slug}/README.md:
    | {n} | {today} | {score_before}% | {score_after}% | {rounds} | ideas/{slug}/sessions/{filename} |
15. Update ideas_index.md with new score and session count.

### Update agent memories

16. Prepare memory-update prompts for all specialists, then launch them IN A SINGLE MESSAGE (parallel).

    For each specialist {name} in roster:
    a. Read .claude/skills/{name}/MEMORY.md. Save as [CUR_MEM_{name}]. If absent, use "".
    b. Collect all messages from this specialist across all rounds as [CONTRIBUTIONS_{name}],
       labeled "Round {n}: {message content}".

    After preparing all prompts, issue ALL Agent calls in ONE message at once (do NOT wait for
    one to finish before issuing the next — they are independent and can run in parallel):
    For each specialist {name}:
    - subagent_type: "{name}"  (e.g. "specialist-finance")
    - description: "Memory update — {Specialist display name}"
    - prompt:
      MODE: memory-update

      [CURRENT MEMORY]
      {[CUR_MEM_{name}]}

      [YOUR CONTRIBUTIONS]
      {[CONTRIBUTIONS_{name}]}

      [SESSION SYNTHESIS]
      {synthesis from the final agora-score-round output}

      [DATE]
      {today's date YYYY-MM-DD}

    c. After all Agent calls return, collect the returned MEMORY.md content from each.
       Write all files in a single Bash call using heredocs — one per file — rather than
       separate Write tool calls. Example:
       ```bash
       cat > .claude/skills/specialist-foo/MEMORY.md << 'EOF'
       {content}
       EOF
       cat > .claude/skills/specialist-bar/MEMORY.md << 'EOF'
       {content}
       EOF
       ```

### Evaluate KPIs and write analytics

17. Evaluate the session KPIs defined in step 5:

    a. For each dimension target in [SESSION_KPIS]:
       - Met:     final_score >= target
       - Partial: final_score > before AND final_score < target
       - Not met: final_score <= before
       Record: {dimension, before, target, after, result}

    b. For each key question, assess from the full transcript whether it was answered:
       - Yes:     a clear, specific answer was established
       - Partial: progress was made but no definitive answer
       - No:      not addressed
       Record: {question, answered: yes|partial|no}

    c. Compute the KPI score:
       kpi_score = (count_met × 1.0 + count_partial × 0.5) / total_kpi_count
       Round to 2 decimal places.

    d. Save as [KPI_RESULTS]: {dimension_results, question_results, kpi_score}

18. Write session analytics — append one JSON line to analytics/sessions.jsonl
    (create the file if it does not exist; create analytics/ directory if needed).
    Use a single Bash call with `>>` rather than a Write tool call:

    {
      "session_id": "{slug}-session-{n}-{YYYYMMDD}",
      "slug": "{slug}",
      "idea_name": "{idea name}",
      "date": "{YYYY-MM-DD}",
      "rounds": {rounds_completed},
      "score_before": {score_before},
      "score_after": {score_after},
      "delta": {score_after - score_before},
      "ended_reason": "{max_rounds|target_reached}",
      "kpi_score": {float 0.0–1.0},
      "kpis": {
        "dimension_targets": [
          {"dimension": "...", "before": N, "target": N, "after": N, "result": "met|partial|not_met"}
        ],
        "questions": [
          {"question": "...", "answered": "yes|partial|no"}
        ]
      },
      "specialists": ["{specialist-name}", ...],
      "specialist_versions": {"{specialist-name}": "{version}", ...}
    }

    Read the version field from each specialist's agent definition at `.claude/agents/{name}.md` frontmatter to populate specialist_versions.

### Print final summary

19. Print:

    ══ Session Complete ══════════════════════════
    Idea: {name}
    Rounds: {n}
    Readiness: {before}% → {after}% (+{delta}%)
    Ended because: {reason}
    Report: ideas/{slug}/sessions/{filename}

    KPI Results ({kpi_score × 100}% achieved):
    • {dimension}: {before}/10 → {after}/10 [{Met|Partial|Not met}] (target was {target}/10)
    • {dimension}: {before}/10 → {after}/10 [{Met|Partial|Not met}]
    • {dimension}: {before}/10 → {after}/10 [{Met|Partial|Not met}]
    • Q: "{question 1}" → {Yes|Partial|No}
    • Q: "{question 2}" → {Yes|Partial|No}

    Weakest dimensions to address next:
    • {dim 1}: {score}/10
    • {dim 2}: {score}/10

    Specialist memories updated: {comma-separated list}

    Run /agora-run-debate {slug} to continue developing this idea.

### Post-session review (opt-in)

20. Print a prompt to the user:

    ── Post-session options ───────────────────────
    • /agora-review-specialists {slug} — review specialist performance, generate improvement proposals
    • /agora-hire-specialists {slug} — check for coverage gaps, generate job posts
    (Skip to save tokens — run them manually at any time.)
    ───────────────────────────────────────────────

    Do NOT invoke either skill automatically. Wait for the user to trigger them.
