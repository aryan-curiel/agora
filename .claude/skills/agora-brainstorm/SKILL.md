---
name: agora-brainstorm
description: Run a full multi-agent brainstorm session to expand an idea's possibility space. Use when the user wants to brainstorm, explore, or generate proposals for an idea. Produces a set of proposals organized by time horizon (quick wins, growth features, moonshots). Does not affect readiness scores.
disable-model-invocation: true
argument-hint: "[idea-id]"
allowed-tools: Read Write
version: 1.0.0
---

## Run a brainstorm session

### Setup

1. Resolve the idea from $ARGUMENTS. If empty, read `ideas_index.md` and ask the user to pick from active ideas.

2. Read `ideas/{slug}/README.md` fully. Note the idea name, description, open questions, and any existing `## Proposals` section. Save as [IDEA_CONTEXT].

3. Determine session number: count files matching `*-brainstorm-*` in `ideas/{slug}/sessions/` + 1. If the directory doesn't exist, session number is 1.

4. Read `max_brainstorm_rounds` from `CLAUDE.md` session defaults (default: 3 if not present).

### Print session header

5. Print:
   ```
   ── Brainstorm Session {n} — {Idea Name} ─────────────────
   Idea: {name}
   Description: {first 2 sentences of description}
   Dreamers: The Futurist · The Builder · The User Advocate · The Connector · The Narrativist
   Skeptic grounding: After rounds 2 and 3
   Rounds: {max_brainstorm_rounds}
   
   {If existing proposals exist: "Existing proposals: {count} — dreamers will not repeat these."}
   ──────────────────────────────────────────────────────────
   ```

### Run rounds

**IMPORTANT: Execute all rounds and all post-session steps without pausing for user confirmation. Do not stop, summarise, or ask "shall I continue?" at any point mid-session.**

For each round (1 through max_brainstorm_rounds):

6. Print a round header:
   ```
   ── Round {n} of {max_brainstorm_rounds} ─────────────────────────────────────
   Focus: {Round 1: "Free divergence — all horizons open" | Round 2: "Cross-pollination — build on each other" | Round 3: "Sharpening — fill thin horizons"}
   ──────────────────────────────────────────────────────────
   ```

7. Determine [HORIZON ASSIGNMENT] for this round:
   - Round 1: `All horizons open`
   - Round 2: `futurist → moonshot; builder → quick-win; user-advocate → growth-feature; connector → growth-feature; narrativist → growth-feature or moonshot`
   - Round 3: Assess which horizon has the fewest proposals so far and direct each dreamer to prioritize it.

8. For each dreamer in order — futurist, builder, user-advocate, connector, narrativist:

   a. Read `.claude/skills/dreamer-{name}/MEMORY.md` if it exists. Load as [YOUR MEMORY].
   
   b. Invoke `/dreamer-{name}` with context containing:
      - [YOUR MEMORY]: {content of their MEMORY.md, if it exists}
      - [IDEA CONTEXT]: {idea name, full description, open questions}
      - [BRAINSTORM HISTORY]: {all proposals generated so far this session, formatted as a list}
      - [HORIZON ASSIGNMENT]: {this round's horizon directive for this dreamer}
      - Round number and any cross-pollination instruction (Round 2+: "You must build on or fork at least one proposal from another dreamer in [BRAINSTORM HISTORY]")
   
   c. Print their output in a panel:
      ```
      ┌─ The {Dreamer Display Name} ─────────────────────────────┐
      │ {response}                                                │
      └────────────────────────────────────────────────────────── ┘
      ```
   
   d. Parse all proposals from their response. For each proposal, record:
      - horizon (quick-win | growth-feature | moonshot)
      - title
      - description
      - dreamer name
      - round number
      Add to [ALL_PROPOSALS].

9. After each round (rounds 2 and 3 only): invoke `/specialist-skeptic` with context:
   ```
   MODE: brainstorm-grounding
   [IDEA CONTEXT]: {idea name and description}
   [ALL PROPOSALS SO FAR]: {full list of proposals from all rounds so far}
   
   You are grounding a brainstorm session, not challenging the original idea.
   Review the proposals above. Flag 2–3 that are structurally broken, already exist as products, or depend on a false premise. Give one sentence per flag.
   End with exactly 2 sharp questions about the most fragile proposals.
   
   Format:
   
   Skeptic Flags:
   - **{Proposal title}**: {one sentence reason}
   
   Questions:
   1. {question?}
   2. {question?}
   ```
   
   Print skeptic output in a panel labeled `┌─ The Skeptic (Grounding) ─...`.
   Record flagged proposal titles and questions as [SKEPTIC_FLAGS] and [SKEPTIC_QUESTIONS].

### Write output

10. Invoke `/agora-write-brainstorm-report` with:
    - slug, session number, date, idea name
    - [ALL_PROPOSALS] organized by horizon
    - [SKEPTIC_FLAGS], [SKEPTIC_QUESTIONS] from rounds 2 and 3
    - Full transcript (all dreamer and skeptic outputs by round)
    
    The skill returns the filename. Save as [REPORT_FILENAME].

11. Update `ideas/{slug}/README.md`:
    
    If a `## Proposals` section already exists, merge new proposals into it:
    - Append new proposals under their horizon heading
    - Tag each new proposal with `(Session {n})`
    - Never delete existing proposals
    
    If no `## Proposals` section exists, insert it between `## Notes` (or `## Open Questions`) and `## Session History`. If neither exists, append at end before any session history section.
    
    Section format:
    ```markdown
    ## Proposals
    
    *Last updated: {YYYY-MM-DD} (Brainstorm Session {n})*
    
    ### Quick Wins (0–3 months)
    - **{title}** (Session {n}): {1-sentence description}
    
    ### Growth Features (3–12 months)
    - **{title}** (Session {n}): {1-sentence description}
    
    ### Moonshots (1+ year)
    - **{title}** (Session {n}): {1-sentence description}
    ```

12. Update `ideas_index.md`:
    - If a `Brainstorms` column exists: increment the count for this idea
    - If the column does not exist: add it between `Sessions` and `Last Updated`, set to 0 for all ideas, then set this idea to 1
    - Update `Last Updated` to today's date for this idea

### Update dreamer memories

13. For each dreamer, trigger a memory update:
    a. Read `.claude/skills/dreamer-{name}/MEMORY.md` — load as [CURRENT MEMORY]. If absent, use empty string.
    b. Collect all proposals from this dreamer across all rounds as [YOUR CONTRIBUTIONS], labeled "Round {n}: {full output}".
    c. Use a brief synthesis of all proposals generated as [SESSION SYNTHESIS].
    d. Invoke `/dreamer-{name}` with:
       - MODE: memory-update
       - [CURRENT MEMORY]: {content from step a}
       - [YOUR CONTRIBUTIONS]: {content from step b}
       - [SESSION SYNTHESIS]: {content from step c}
       - [DATE]: {today's date YYYY-MM-DD}
    e. The dreamer returns ONLY the updated MEMORY.md content.
    f. Collect all updated MEMORY.md contents, then write them in a single Bash call using heredocs:
       ```bash
       cat > .claude/skills/dreamer-futurist/MEMORY.md << 'EOF'
       {content}
       EOF
       cat > .claude/skills/dreamer-builder/MEMORY.md << 'EOF'
       {content}
       EOF
       {... repeat for all 5 dreamers ...}
       ```

### Write analytics

14. Append one JSON line to `analytics/brainstorms.jsonl` (create the file if it does not exist):
    ```bash
    echo '{...}' >> analytics/brainstorms.jsonl
    ```
    
    JSON structure:
    ```json
    {
      "session_id": "{slug}-brainstorm-{n}-{YYYYMMDD}",
      "slug": "{slug}",
      "idea_name": "{idea name}",
      "date": "{YYYY-MM-DD}",
      "rounds": {max_brainstorm_rounds},
      "proposals_generated": {total count},
      "proposals_by_horizon": {
        "quick_win": {count},
        "growth_feature": {count},
        "moonshot": {count}
      },
      "flagged_proposals": {count of skeptic flags},
      "dreamers": ["dreamer-futurist", "dreamer-builder", "dreamer-user-advocate", "dreamer-connector", "dreamer-narrativist"],
      "dreamer_versions": {
        "dreamer-futurist": "{version from SKILL.md frontmatter}",
        "dreamer-builder": "{version}",
        "dreamer-user-advocate": "{version}",
        "dreamer-connector": "{version}",
        "dreamer-narrativist": "{version}"
      }
    }
    ```

14b. For each dreamer, append one JSON line to `analytics/dreamers.jsonl` (create if it does not exist).
    Evaluate each dreamer's contributions across all rounds using these criteria:

    **Scores (1–5):**
    - `originality`: Did they propose directions not already obvious from the idea or prior rounds?
    - `specificity`: Were they concrete — naming mechanisms, timeframes, technologies, or behaviors (not vague generalities)?
    - `cross_pollination`: Did they explicitly build on or fork from another dreamer's proposals in Round 2+?
    - `horizon_adherence`: Did they follow their horizon assignment? (round 1 is open; rounds 2–3 have directed assignments)

    **Counts:**
    - `proposals_count`: Total proposals this dreamer generated across all rounds
    - `flagged_count`: How many of their proposals were named in a Skeptic flag

    **Overall:** Average of the four numeric scores, rounded to 2 decimal places.

    JSON structure per dreamer:
    ```json
    {
      "session_id": "{slug}-brainstorm-{n}-{YYYYMMDD}",
      "date": "{YYYY-MM-DD}",
      "dreamer": "dreamer-{name}",
      "version": "{version from SKILL.md frontmatter}",
      "scores": {
        "originality": {1–5},
        "specificity": {1–5},
        "cross_pollination": {1–5},
        "horizon_adherence": {1–5},
        "word_count_compliance": {true|false}
      },
      "proposals_count": {integer},
      "flagged_count": {integer},
      "overall": {average of four numeric scores, 2 decimal places},
      "proposal_written": false,
      "proposal_file": null
    }
    ```

### Print final summary

15. Print:
    ```
    ══ Brainstorm Complete ═══════════════════════════════════
    Idea: {name}
    Session: {n}
    Proposals generated: {total}
      Quick wins:       {count}
      Growth features:  {count}
      Moonshots:        {count}
    Skeptic flags:      {count}
    Report: {REPORT_FILENAME}
    
    Strongest quick win:       {title}
    Most promising growth:     {title}
    Moonshot to track:         {title}
    
    Run /agora-run-debate {slug} to develop any of these further.
    ══════════════════════════════════════════════════════════
    ```
