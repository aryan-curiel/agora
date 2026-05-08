# Changelog — apply-agent-update

## [1.1.0] — 2026-05-08

### Added
- Step 4b: for `major` change-type proposals, prompt the user to optionally validate the new design with `/anthropic-architect` before applying changes. Includes check for "Architectural Notes" section in the proposal.

---

## [1.0.0] — 2026-05-08

### Added
- Initial version: Applies a pending proposal to a skill definition, bumps the version in frontmatter, cascades updates to agents affected by breaking changes, marks the proposal as applied, and prepends a CHANGELOG entry.

---
