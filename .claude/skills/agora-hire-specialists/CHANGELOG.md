# Changelog — agora-hire-specialists

## [1.0.0] — 2026-05-09

### Added
- Initial version: analyzes a completed debate session to identify expertise gaps not covered by the current specialist roster.
- Two-filter gate: candidates must pass both immediate session impact AND cross-idea reusability before a job-post is written.
- Writes `job-posts/specialist-{slug}.md` per approved candidate, using a structured template that captures role, knowledge domain, debate behavior, output format, selection criteria, memory update mode, and a concrete example contribution.
- Default stance: no specialists proposed unless both filters clearly pass — avoids roster inflation.
- Invoked automatically by agora-run-debate (step 21) and available as a standalone user-invocable skill.
