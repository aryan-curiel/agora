# Changelog — agora-score-round

## [1.1.0] — 2026-05-10

### Fixed
- Eliminated nested sub-skill invocation of agora-meta-specialist. Previously agora-run-debate → agora-score-round → agora-meta-specialist created a 2-level fork chain that broke on the turn boundary — agora-score-round could never return results, causing the debate session to stall after Round 1. Now agora-score-round embeds the scoring logic directly and returns results in one shot.

## [1.0.0] — 2026-05-08

### Added
- Initial version: Orchestrator that invokes agora-meta-specialist with round messages, parses the JSON response, computes the readiness percentage, and returns structured scores to agora-run-debate.

---
