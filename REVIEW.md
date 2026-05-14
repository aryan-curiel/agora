# Code Review: `.claude/` Folder — Agora Skills & Agents

**Date:** 2026-05-14

## Overview

This is a well-architected multi-agent system for developing startup ideas through structured debate. The working tree reflects an **in-progress migration** from skill-based agent invocation (`/specialist-{name}`) to the Claude Code Agent tool (`subagent_type: "{name}"`), using `.claude/agents/` definition files. The core logic is sound and the improvement loop (review → propose → apply → analyze) is genuinely sophisticated.

---

## Critical Issues

**1. `agora-meta-specialist` is a dead skill with no callers**

`agora-score-round/SKILL.md` now opens with "Do NOT invoke any sub-skills. Perform scoring directly." It contains a full copy of the scoring rubric. `agora-meta-specialist/SKILL.md` is identical but adds nothing. It's registered in the system skill list and will confuse future skill selection. Delete or explicitly mark `deprecated` in the description.

**2. `.claude/agents/` is untracked — the migration is half-committed**

`git status` shows `?? .claude/agents/` (untracked directory). The dreamer and specialist SKILL.md files are deleted from the index (e.g. `D .claude/skills/dreamer-builder/SKILL.md`) but the replacement `.claude/agents/` definitions haven't been staged. If someone pulls this branch, `agora-run-debate` and `agora-brainstorm` will call `subagent_type: "dreamer-futurist"` but no matching agent file will exist. Commit the agents directory.

**3. Inconsistent version source after the agents migration**

`agora-run-debate` step 18 says:
> "Read the version field from each specialist's SKILL.md frontmatter... Since specialists are now agent definition files in `.claude/agents/`, read their version from `.claude/agents/{name}.md` frontmatter instead."

But `agora-review-specialists` step 3 still reads from `.claude/skills/{specialist-name}/SKILL.md` for the version. One is now an agents file, the other is a skills file — they may not have the same version after the migration. Resolve to a single source of truth (the agents file) and update both skills.

---

## Moderate Issues

**4. `agora-run-debate` step 18 has a migration comment baked into prose**

The phrase "Since specialists are now agent definition files in `.claude/agents/`, read their version from `.claude/agents/{name}.md` frontmatter instead." is a migration note embedded as permanent instruction. It will confuse anyone reading the skill in 6 months. Collapse the two sentences into one clean instruction pointing only at `.claude/agents/`.

**5. `settings.local.json` has two stale permissions**

```json
"Bash(mkdir -p /Users/aryancuriel/Development/Projects/agora/.claude/skills/review-agents)",
"Bash(mkdir -p /Users/aryancuriel/Development/Projects/agora/.claude/skills/apply-agent-update)",
```

These paths (`review-agents`, `apply-agent-update`) no longer exist — these skills were renamed to `agora-review-specialists` and `agora-apply-specialist-update`. Dead permissions clutter the allowlist.

**6. `agora-score-round` has `constraint_overrides` in its output schema; `agora-meta-specialist` does not**

Since the meta-specialist skill is dead (see issue #1), this is a non-issue in practice — but it reinforces that the two files have drifted and the meta-specialist needs to be removed.

**7. `dreamer-*` analytics schema has `word_count_compliance` nested inside `scores`; specialist analytics does not match**

`analytics/dreamers.jsonl` records `word_count_compliance: true|false` inside the `scores` object. The parallel `analytics/specialists.jsonl` schema in `agora-review-specialists` also has `word_count_compliance` but as a standalone top-level field outside `scores`. Inconsistent nesting — pick one structure for both.

---

## Minor Issues

**8. `agora-brainstorm` is missing a `CHANGELOG.md`**

The unstaged diff bumps version to `1.1.0` and adds `Agent` to `allowed-tools`. That's correct and appropriate. But there is no `CHANGELOG.md` for `agora-brainstorm` — all other skills with version history have one. Add one to match conventions.

**9. `agora-lead-specialist` uses `context: fork` but no `tools:` field**

The lead specialist needs to `Read ideas/$ARGUMENTS/README.md`. With `context: fork` it runs as a skill (inherits the caller's context and tools), so this works — but it's implicit. The `agora-score-round` skill also omits an explicit context field. Adding explicit `context:` declarations would reduce ambiguity for anyone maintaining these files.

**10. `agora-hire-specialists` summary omits Filter 2 rationale**

Step 12's "Not hired" section shows which filter failed. However the "Hired" section only shows `impact-rationale` (Filter 1). The `reusability-rationale` (Filter 2) isn't shown even though it's the harder filter to pass. Including both in the summary would make the hiring decision legible at a glance.

**11. `agora-brainstorm` step 9 — Skeptic prompt omits its own MEMORY.md**

The Skeptic is invoked for brainstorm grounding but its MEMORY.md is never read or passed in context. All other Skeptic invocations (in `agora-run-debate`) include `[YOUR MEMORY]`. The Skeptic's accumulated knowledge about failed proposal patterns is particularly valuable for grounding — this omission means it operates without institutional memory in brainstorm mode.

---

## Structural Strengths

- The **debate (sequential) vs. brainstorm (parallel)** distinction is architecturally correct — specialists need to react to each other, dreamers don't.
- The **KPI → evaluate → analytics** pipeline in `agora-run-debate` is production-quality. Steps 17–18 close the feedback loop properly.
- The **proposal/apply/changelog** cycle for specialist improvement is sophisticated and self-consistent — the "check for existing pending proposals before creating a new one" rule in `agora-review-specialists` is especially good.
- The **two-filter hiring gate** (immediate impact + cross-idea reusability) prevents roster bloat.
- **Memory scoping** (no idea-specific details in agent memory) is a smart constraint that keeps memories portable.

---

## Action Summary

| Priority | Action |
|---|---|
| Critical | Delete or deprecate `agora-meta-specialist/SKILL.md` |
| Critical | Commit `.claude/agents/` directory — migration is blocking |
| Critical | Align `agora-review-specialists` to read versions from `.claude/agents/` |
| Moderate | Remove migration note from `agora-run-debate` step 18 |
| Moderate | Clean up two stale entries in `settings.local.json` |
| Moderate | Fix `word_count_compliance` nesting inconsistency in analytics schemas |
| Minor | Add `CHANGELOG.md` for `agora-brainstorm` |
| Minor | Pass Skeptic MEMORY.md in brainstorm grounding invocations (step 9) |
| Minor | Show both filter rationales in `agora-hire-specialists` summary output |
