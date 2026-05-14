# Changelog — agora-review-specialists

## [1.3.0] — 2026-05-14

### Changed
- Step 3: Read agent definitions from `.claude/agents/{specialist-name}.md` instead of `.claude/skills/{specialist-name}/SKILL.md` — aligns with the migration of specialist instructions to the agents directory.
- Step 7: Read `version` field from `.claude/agents/{specialist-name}.md` frontmatter instead of SKILL.md.
- Step 9: Analytics `version` field now sourced from `.claude/agents/{specialist-name}.md` frontmatter.
- Step 9: `word_count_compliance` moved out of the `scores` object and made a top-level field in the analytics record — consistent with the dreamer analytics schema in `agora-brainstorm`.
- Removed stale reference to `agora-meta-specialist` from the `major` change-type description (skill deleted — scoring is now inline in `agora-score-round`).

---

## [1.2.0] — 2026-05-09

### Added
- Step 8-pre: Before writing any proposal, scan the specialist's skill directory for existing `PROPOSAL-v*.md` files with `status: pending`. If found, update the existing proposal in place rather than creating a new one. If the new analysis requires a higher version bump, the file is renamed to the new version and the old file is deleted.

---

## [1.1.0] — 2026-05-08

### Added
- Step 7b: for `major` change-type proposals, assess whether the structural changes warrant architecture review and flag in the summary with "consider /knowledge-architect before applying".
- Added optional **Architectural Notes** section to the proposal template (major changes only) to document whether `/knowledge-architect` should be consulted before applying.
- Print summary now includes per-proposal `⚠` flags for major restructures.

---

## [1.0.0] — 2026-05-08

### Added
- Initial version: Post-session agent reviewer that evaluates each specialist's performance against their SKILL.md instructions, determines version bump type, and writes PROPOSAL files for agents that need improvement.

---
