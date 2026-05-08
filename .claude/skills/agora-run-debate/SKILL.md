---
name: agora-run-debate
description: Run a full multi-agent debate session to develop an idea. Use when the user wants to debate, develop, work on, or improve an idea. This is the core workflow of Agora.
disable-model-invocation: true
argument-hint: "[idea-id]"
allowed-tools: Read Write
version: 1.1.0
---

## Run a debate session

### Setup

1. Resolve the idea from $ARGUMENTS. If empty, read ideas_index.md and ask the user to pick from active ideas.
2. Read ideas/{slug}/README.md fully. Note current readiness score and breakdown.
3. Determine session number: count existing rows in the idea's Session History table + 1.
4. Read .claude/skills/agora-lead-specialist/SKILL.md to understand how to invoke the lead agent.

### Invoke the lead agent

5. Invoke /agora-lead-specialist with the idea slug as argument.
   The lead agent returns a JSON array of specialist skill names to include this session.
   Example: ["specialist-skeptic", "specialist-tech-lead", "specialist-market-analyst", "specialist-finance"]
   Save this as the roster for this session.

### Run debate rounds

Default: 3 rounds. Check CLAUDE.md for configured limits.

For each round:

6. Print a round header: "── Round {n} of {max} ──────────────────────"

7. For each specialist in the roster:
   a. Read .claude/skills/{specialist-name}/MEMORY.md — if the file exists, load its content as [YOUR MEMORY].
      If the file does not exist, omit [YOUR MEMORY] from the context.
   b. Invoke the specialist skill as /specialist-{name} with context containing:
      - [YOUR MEMORY]: {content of their MEMORY.md, if it exists}
      - The idea name and full description
      - Current readiness breakdown (scores only, not full file)
      - All messages from previous rounds this session (last 10 messages max for context)
      - Messages from earlier this round (so each specialist sees what others said)
      - Instruction: "Build on what others said. Focus on what has NOT been addressed yet."
   c. After each specialist responds, print their output in a panel:
      ┌─ {Specialist Name} ─────────────────────────────┐
      │ {response}                                       │
      └──────────────────────────────────────────────────┘
   d. Add their message to the round message list.

8. After all specialists in the round have responded, invoke /agora-score-round with:
   - The idea slug
   - All messages from this round
   - Current scores from the idea file

9. /agora-score-round returns updated scores and synthesis. Print a milestone update:

   ── Round {n} complete ──────────────────────────
   Readiness: {old}% → {new}%

   {synthesis paragraph}

   Dimension progress:
   {updated breakdown table with █░ bars}

   Open questions remaining:
   • {question 1}
   • {question 2}
   • {question 3}

10. Update ideas/{slug}/README.md with new scores, open questions, and best answers.

11. Check termination:
    - If rounds completed = max rounds → end, reason: "max_rounds"
    - If readiness >= 85% → end, reason: "target_reached"
    - Otherwise continue to next round.

### Finish

12. Invoke /agora-write-report with the session data.
13. Update the Session History table in ideas/{slug}/README.md:
    | {n} | {today} | {score_before}% | {score_after}% | {rounds} | ideas/{slug}/sessions/{filename} |
14. Update ideas_index.md with new score and session count.

### Update agent memories

15. For each specialist in the roster, trigger a memory update:
    a. Read .claude/skills/{specialist-name}/MEMORY.md — load its content as [CURRENT MEMORY].
       If the file does not exist, use empty string.
    b. Collect all messages from this specialist across all rounds as [YOUR CONTRIBUTIONS],
       labeled "Round {n}: {message content}".
    c. Use the synthesis from the final agora-score-round output as [SESSION SYNTHESIS].
    d. Invoke /specialist-{name} with:
       - MODE: memory-update
       - [CURRENT MEMORY]: {content from step a}
       - [YOUR CONTRIBUTIONS]: {content from step b}
       - [SESSION SYNTHESIS]: {content from step c}
       - [DATE]: {today's date YYYY-MM-DD}
    e. The specialist returns ONLY the updated MEMORY.md content (a markdown document).
    f. Write the returned content to .claude/skills/{specialist-name}/MEMORY.md.

16. Print final summary:

    ══ Session Complete ══════════════════════════
    Idea: {name}
    Rounds: {n}
    Readiness: {before}% → {after}% (+{delta}%)
    Ended because: {reason}
    Report: ideas/{slug}/sessions/{filename}

    Weakest dimensions to address next:
    • {dim 1}: {score}/10
    • {dim 2}: {score}/10

    Specialist memories updated: {comma-separated list of specialists whose MEMORY.md was written}

    Run /agora-run-debate {slug} to continue developing this idea.

### Post-session review

17. Invoke /agora-review-specialists {slug} automatically.
    Pass the slug as the argument so the skill resolves the most recent session file.
    This step is mandatory — do not skip it even if the session ended early.
