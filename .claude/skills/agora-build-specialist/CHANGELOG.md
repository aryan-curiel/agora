# Changelog — agora-build-specialist

## [1.0.0] — 2026-05-10

### Added
- Initial version: builds a new specialist from a `job-posts/specialist-{slug}.md` file.
- Research phase: conducts 4 targeted web searches and reads 4-6 sources to ground the specialist in real domain knowledge — named frameworks, failure modes, practitioner benchmarks.
- Writes `specialist-{slug}/SKILL.md` following the exact pattern of existing specialists, with instructions informed by research findings rather than generic role descriptions.
- Reference file support: for knowledge-heavy domains, writes up to 2 structured `references/*.md` files and patches `agora-run-debate` once to load them as `[DOMAIN REFERENCES]` context — parallel to how `MEMORY.md` is loaded as `[YOUR MEMORY]`.
- Registers the new specialist in `agora-lead-specialist` (minor bump) with selection criteria from the job-post.
- Marks the job-post `status: built` with `built-date`.

---
