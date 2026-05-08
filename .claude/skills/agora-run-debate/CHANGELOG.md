# Changelog — agora-run-debate

## [1.1.0] — 2026-05-08

### Changed
- Specialist invocation (step 7): now reads each agent's `MEMORY.md` before invoking them and passes its content as `[YOUR MEMORY]` in the context, so agents apply accumulated cross-session patterns during debate rounds.

### Added
- Memory update phase (step 15): after agora-write-report and index updates, invokes each specialist in `MODE: memory-update` with their contributions from this session, receives updated `MEMORY.md` content, and writes it to each agent's skill folder.
- Final summary now lists which agent memories were updated.

---

## [1.0.0] — 2026-05-08

### Added
- Initial version: Core orchestrator that runs multi-round debates — invokes agora-lead-specialist for roster selection, runs specialist agents per round, scores each round via agora-score-round/agora-meta-specialist, and finalizes via agora-write-report.

---
