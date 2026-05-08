# Memory — The Product Manager

*Last updated: 2026-05-08*

## KPI Anti-Patterns to Catch Early

- Completion rates and click-through metrics are vanity metrics for tool/workflow products — they measure curiosity, not value.
- Readiness delta (e.g., +15 points per session) is measurable and meaningful but gameable if the scoring model inflates.
- **Behavioral signals are superior KPIs**: second-session rate within 14 days, share rate within 48h, and median session duration are harder to fake and reflect genuine habit formation.
- "Good retention" without a timeframe and a denominator is not a KPI. Always require: metric name + threshold + timeframe + measurement method.

## PoC Scope Rules

- The PoC must prove the core assumption, not demonstrate the full product. One session with real users beats a polished demo with zero external usage.
- For debate/tool products: the PoC success condition should be a behavioral repeat signal — one session is curiosity, two sessions is habit. Use "X of N users run a second session unprompted within 14 days" as the bar.
- Features that consistently get added to PoC scope prematurely: hosted wrappers, team/multi-user features, export formats, custom agent configuration. Cut all of these to V1 or later.
- A single non-builder user completing the full flow and reporting it influenced a real decision is a stronger PoC proof point than aggregate stats from 3 internal runs.

## Roadmap Phase Discipline

- PoC: existing system or minimal wrapper — test the core assumption with real (non-builder) users this weekend.
- MVP: the smallest hosted/shareable version with a paywall signal (even a waitlist + pricing page counts). $15–$25/session pack is a defensible entry price point for workflow tools.
- V1: unlocks configuration, team features, and export — this is what you charge recurring subscription for ($35–$50/mo range for knowledge worker tools).
- Do not advance past PoC until the control test (single prompt vs. multi-agent) has been run. Skipping this is the most common roadmap mistake in AI-native tool ideas.

## Riskiest Assumptions by Idea Type

### AI-native workflow/debate tools
- **Core**: multi-agent debate produces meaningfully better output than a single well-prompted LLM. This is unproven until tested with a blind control.
- **Secondary**: users will return after the novelty wears off (session 1 is exploration, session 2 is the real test).
- **Tertiary**: the debate feels like genuine tension, not scripted theater. If users perceive it as AI talking to itself, trust collapses and the product loses its differentiator.

### General patterns across idea types
- Marketplace/network ideas: supply-side chicken-and-egg is always the riskiest assumption; validate supply commitment before building demand-side features.
- Productivity tools: "saves time" is not validated until you measure before/after task duration with the same user.
- Community/social: engagement metrics from early adopters (builders, enthusiasts) do not predict mainstream retention.

## Scope Decisions That Were the Right Call

- Enforcing a control test before any further build investment is always correct for AI quality claims — recommend this in round 1, not round 3.
- Deferring session replay surface and team features to post-MVP was correct; both add significant complexity with no PoC learning value.
- Anchoring the PoC success condition to unprompted repeat usage (not just completion) correctly filters signal from noise.
