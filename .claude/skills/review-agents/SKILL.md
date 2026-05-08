---
name: review-agents
description: Reviews specialist agent performance after a completed debate session and writes improvement proposals. Use after a debate session to improve agent quality over time.
version: 1.1.0
argument-hint: "[idea-slug] [session-number]"
allowed-tools: Read Write
---

## Review agent performance

### Setup

1. Resolve the session from $ARGUMENTS:
   - If `[idea-slug] [session-number]` provided, find `ideas/{slug}/sessions/{slug}-session-{n}-*.md`
   - If only slug provided, use the most recent session file in `ideas/{slug}/sessions/`
   - If no arguments, read `ideas_index.md` and ask the user to pick an idea and session

2. Read the session report fully. Extract:
   - Which agents participated (from the "Agents:" header line)
   - All round transcripts (every agent panel in every round)
   - Readiness before/after and per-dimension changes
   - Synthesis and open questions from the final round

### Analyze each agent

3. For each agent in the session roster, read `.claude/skills/{agent-name}/SKILL.md`.

4. Review all of that agent's contributions across all rounds in the transcript. Evaluate:

   **Adherence** — Did they follow their stated role, output structure, and constraints?
   **Specificity** — Did they name real things (technologies, platforms, numbers, companies) or stay vague?
   **Novelty** — Did they add new information each round, or repeat points already made?
   **Word count** — Did they stay within the stated 250-400 word limit (if applicable)?
   **Impact** — Did their contributions measurably raise any readiness dimension score?
   **Responsiveness** — Did they acknowledge and build on relevant points from the same round?

5. For each criterion, note specific evidence: which round, which quote or paraphrase.

6. Assign an overall severity:
   - `none`: Agent performed as expected — no proposal needed
   - `minor`: Small improvements — tighter wording, better examples, slight behavior nudge
   - `moderate`: Behavior gap — agent is not following part of its instructions consistently
   - `major`: Significant dysfunction — agent consistently underperforms its role across rounds

### Determine version bump

7. For agents that need changes, choose a version bump type:
   - `patch` (x.x.N): Minor fixes and wording improvements — no behavior change
   - `minor` (x.N.0): Behavior changes, added guidance, or new constraints — output format unchanged
   - `major` (N.0.0): Output format or structure changes that could break callers (e.g., meta-agent, score-round, run-debate parse this agent's output)

   Read `version` from `.claude/skills/{agent-name}/SKILL.md` frontmatter.
   If no `version` field exists, treat the current version as `1.0.0`.

   To compute the next version from current `MAJOR.MINOR.PATCH`:
   - patch bump: increment PATCH, keep MAJOR.MINOR
   - minor bump: increment MINOR, reset PATCH to 0
   - major bump: increment MAJOR, reset MINOR and PATCH to 0

### Check for architectural review need

7b. For any agent assigned `major` change-type (output format or structural changes):
   - Assess whether the proposed restructuring introduces new interaction patterns or changes how other agents consume this agent's output.
   - If the restructuring is complex, add an **Architectural Notes** section to that agent's proposal (see step 8a template).
   - Flag it in the print summary with: "⚠ Major restructure — consider /anthropic-architect before applying"

### Write proposal files

8. For each agent with severity `minor`, `moderate`, or `major`:
   a. Write `.claude/skills/{agent-name}/PROPOSAL-v{next-version}.md` with this exact structure:

---
agent: {agent-name}
current-version: {current}
proposed-version: {next-version}
change-type: {patch|minor|major}
session: ideas/{slug}/sessions/{filename}
date: {YYYY-MM-DD}
status: pending
---

## Proposed Changes to {agent-name}

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
- **Affected agents:** {comma-separated list of agent names, or "none"}
- **What breaks:** {description of what callers would need to update, or "n/a"}

### Recommended Testing
{One sentence on how to verify the change worked in the next session}

### Architectural Notes *(major change-type only — omit for patch/minor)*
{One sentence on whether /anthropic-architect should be consulted to validate the new structure before applying, and why. Example: "This restructures the output schema consumed by meta-agent — validate the new format with /anthropic-architect to confirm it follows progressive-disclosure best practices."}

   b. Do not create a proposal file for agents with severity `none`.

### Print summary

9. Print:

   ── Agent Review Complete ────────────────────────────
   Session: {filename}
   Agents reviewed: {n}

   Proposals written:
   {for each proposal: • {agent-name} v{current} → v{proposed} ({change-type}): {one-line summary}}
   {for each major proposal: ⚠ {agent-name}: major restructure — consider /anthropic-architect before applying}

   No changes needed:
   {for each agent with no proposal: • {agent-name}: performed as expected}

   To apply a proposal: /apply-agent-update {agent-name}
   ────────────────────────────────────────────────────
