---
name: agora-review-specialists
description: Reviews specialist agent performance after a completed debate session and writes improvement proposals. Use after a debate session to improve agent quality over time.
version: 1.3.0
argument-hint: "[idea-slug] [session-number]"
allowed-tools: Read Write
author: Aryan Curiel
---

## Review agent performance

### Setup

1. Resolve the session from $ARGUMENTS:
   - If `[idea-slug] [session-number]` provided, find `ideas/{slug}/sessions/{slug}-session-{n}-*.md`
   - If only slug provided, use the most recent session file in `ideas/{slug}/sessions/`
   - If no arguments, read `ideas_index.md` and ask the user to pick an idea and session

2. Read the session report fully. Extract:
   - Which specialists participated (from the "Specialists:" header line)
   - All round transcripts (every specialist panel in every round)
   - Readiness before/after and per-dimension changes
   - Synthesis and open questions from the final round

### Analyze each specialist

3. For each specialist in the session roster, read `.claude/agents/{specialist-name}.md`.

4. Review all of that agent's contributions across all rounds in the transcript. Evaluate:

   **Adherence** — Did they follow their stated role, output structure, and constraints?
   **Specificity** — Did they name real things (technologies, platforms, numbers, companies) or stay vague?
   **Novelty** — Did they add new information each round, or repeat points already made?
   **Word count** — Did they stay within the stated 250-400 word limit (if applicable)?
   **Impact** — Did their contributions measurably raise any readiness dimension score?
   **Responsiveness** — Did they acknowledge and build on relevant points from the same round?

5. For each criterion, note specific evidence: which round, which quote or paraphrase.

6. Assign an overall severity:
   - `none`: Specialist performed as expected — no proposal needed
   - `minor`: Small improvements — tighter wording, better examples, slight behavior nudge
   - `moderate`: Behavior gap — specialist is not following part of its instructions consistently
   - `major`: Significant dysfunction — specialist consistently underperforms its role across rounds

### Determine version bump

7. For agents that need changes, choose a version bump type:
   - `patch` (x.x.N): Minor fixes and wording improvements — no behavior change
   - `minor` (x.N.0): Behavior changes, added guidance, or new constraints — output format unchanged
   - `major` (N.0.0): Output format or structure changes that could break callers (e.g., agora-score-round, agora-run-debate parse this agent's output)

   Read `version` from `.claude/agents/{specialist-name}.md` frontmatter.
   If no `version` field exists, treat the current version as `1.0.0`.

   To compute the next version from current `MAJOR.MINOR.PATCH`:
   - patch bump: increment PATCH, keep MAJOR.MINOR
   - minor bump: increment MINOR, reset PATCH to 0
   - major bump: increment MAJOR, reset MINOR and PATCH to 0

### Check for architectural review need

7b. For any agent assigned `major` change-type (output format or structural changes):
   - Assess whether the proposed restructuring introduces new interaction patterns or changes how other agents consume this agent's output.
   - If the restructuring is complex, add an **Architectural Notes** section to that agent's proposal (see step 8a template).
   - Flag it in the print summary with: "⚠ Major restructure — consider /knowledge-architect before applying"

### Check for existing pending proposals

8-pre. Before writing any proposal file, scan `.claude/skills/{specialist-name}/` for existing `PROPOSAL-v*.md` files:
   - Read each matching file and check its `status` field in the frontmatter.
   - If a file has `status: pending`, it is an unapplied proposal — **update it instead of creating a new one**.
   - Compare the `change-type` in the existing proposal against the newly determined change-type:
     - If the new analysis requires a **higher** bump level (patch → minor, patch → major, minor → major), recompute the proposed version from the current skill version using the higher change-type.
     - If the new analysis requires the **same or lower** bump level, keep the version from the existing proposal.
   - If the proposed version changed, delete the old `PROPOSAL-v{old-version}.md` file and write a new `PROPOSAL-v{new-version}.md`.
   - If the proposed version is unchanged, overwrite the existing file in place.
   - Set the `date` field to today's date in the updated proposal.
   - If `status: applied` or no proposal file exists at all, proceed to create a new proposal file as normal.

### Write proposal files

8. For each specialist with severity `minor`, `moderate`, or `major`:
   a. Write `.claude/skills/{specialist-name}/PROPOSAL-v{next-version}.md` with this exact structure:

---
specialist: {specialist-name}
current-version: {current}
proposed-version: {next-version}
change-type: {patch|minor|major}
session: ideas/{slug}/sessions/{filename}
date: {YYYY-MM-DD}
status: pending
---

## Proposed Changes to {specialist-name}

### Summary
{1-2 sentences: why the agent underperformed and what the fix addresses}

### Observed Issues

{One entry per issue:}
- **[{minor|moderate|major}]** {Description of the observed behavior and why it is a problem.}
  *Evidence: Round {n} — "{brief quote or paraphrase from transcript}"*

### Proposed Skill Changes

{One section per discrete change:}
#### Change {n}: {Short title}

**Current instruction:**
```
{exact text block from the SKILL.md that needs to change}
```

**Proposed instruction:**
```
{replacement text}
```

**Rationale:** {Why this change addresses the observed issue and what behavior it drives}

### Breaking Change Analysis

- **Breaking:** {yes / no}
- **Affected specialists:** {comma-separated list of specialist names, or "none"}
- **What breaks:** {description of what callers would need to update, or "n/a"}

### Recommended Testing
{One sentence on how to verify the change worked in the next session}

### Architectural Notes *(major change-type only — omit for patch/minor)*
{One sentence on whether /knowledge-architect should be consulted to validate the new structure before applying, and why. Example: "This restructures the output schema consumed by agora-meta-specialist — validate the new format with /knowledge-architect to confirm it follows progressive-disclosure best practices."}

   b. Do not create a proposal file for agents with severity `none`.

### Write specialist analytics

9. Append one JSON line per specialist to analytics/specialists.jsonl
   (create the file if it does not exist; create analytics/ directory if needed):

   For each specialist reviewed:
   {
     "session_id": "{slug}-session-{n}-{YYYYMMDD}",
     "date": "{YYYY-MM-DD}",
     "specialist": "{specialist-name}",
     "version": "{version from .claude/agents/{specialist-name}.md frontmatter}",
     "scores": {
       "adherence": {1–5},
       "specificity": {1–5},
       "novelty": {1–5},
       "responsiveness": {1–5},
       "impact": {1–5}
     },
     "word_count_compliance": {true|false},
     "overall": {average of the five numeric scores, rounded to 1 decimal},
     "severity": "{none|minor|moderate|major}",
     "proposal_written": {true|false},
     "proposal_file": "{path to PROPOSAL file, or null}"
   }

   Score rubric (1–5):
   - adherence: Did they follow their stated role and output structure?
   - specificity: Did they name real technologies, numbers, companies, not vague generalities?
   - novelty: Did they introduce new information each round vs. repeat prior points?
   - responsiveness: Did they acknowledge and build on what other specialists said?
   - impact: Did their contributions measurably raise any readiness dimension score?

### Print summary

10. Print:

    ── Specialist Review Complete ────────────────────────────
    Session: {filename}
    Specialists reviewed: {n}

    Proposals written:
    {for each proposal: • {specialist-name} v{current} → v{proposed} ({change-type}): {one-line summary}}
    {for each major proposal: ⚠ {specialist-name}: major restructure — consider /knowledge-architect before applying}

    No changes needed:
    {for each specialist with no proposal: • {specialist-name}: performed as expected}

    Analytics written: analytics/specialists.jsonl (+{n} records)

    To apply a proposal: /agora-apply-specialist-update {specialist-name}
    ────────────────────────────────────────────────────
