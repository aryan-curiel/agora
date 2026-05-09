# Changelog — agora-review-specialists

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
