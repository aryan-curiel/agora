# Changelog — agora-brainstorm

## [1.1.0] — 2026-05-14

### Changed
- Step 8: Dreamers are now invoked in parallel via the Agent tool (all 5 in a single message) instead of sequentially with skill invocations. Dreamers cross-pollinate across rounds via [BRAINSTORM HISTORY], not within a round, so concurrent execution is safe and faster.
- Added `Agent` to `allowed-tools`.
- Step 9: Skeptic grounding now reads `.claude/skills/specialist-skeptic/MEMORY.md` before the Agent call and passes it as `[YOUR MEMORY]`, consistent with how debate sessions invoke the Skeptic.
- Step 13: Dreamer memory updates are now issued in a single parallel message via the Agent tool.

### Fixed
- `word_count_compliance` moved out of the `scores` object in the `analytics/dreamers.jsonl` schema — it is now a top-level field alongside `overall`, consistent with the specialist analytics schema.

---

## [1.0.0] — 2026-05-09

### Added
- Initial version: multi-agent brainstorm skill with 5 dreamer personas (Futurist, Builder, User Advocate, Connector, Narrativist) running across 3 rounds with Skeptic grounding after rounds 2 and 3.
- Proposals organized by time horizon: quick-win, growth-feature, moonshot.
- Dreamer memory system using `.claude/skills/dreamer-{name}/MEMORY.md`.
- Session reports written via `agora-write-brainstorm-report`.
- Analytics written to `analytics/brainstorms.jsonl` and `analytics/dreamers.jsonl`.

---
