# Changelog — specialist-finance

## [1.2.0] — 2026-05-09

### Changed
- Added explicit per-unit margin check to pricing proposal step: for every paid tier with a session or usage cap, Finance must compute revenue-per-unit minus per-session API/infra cost and flag any tier with gross margin below 30% as broken pricing before endorsing it.

**Source:** Proposal `PROPOSAL-v1.2.0.md` — session `ideas/agora/sessions/agora-session-1-20260508.md`

---

## [1.1.0] — 2026-05-08

### Added
- Memory system: reads `[YOUR MEMORY]` from context at the start of each debate contribution to apply accumulated patterns about forgotten cost categories and pricing model failure modes.
- Memory update mode: when invoked with `MODE: memory-update` by agora-run-debate after session completion, generates an updated `MEMORY.md` capturing budget calibration patterns, revenue timeline realism, and recurring financial blind spots.

---

## [1.0.0] — 2026-05-08

### Added
- Initial version: Finance specialist that proposes monetization models with concrete pricing, estimates budget per phase (PoC/MVP/V1), and identifies the biggest financial risk.

---
