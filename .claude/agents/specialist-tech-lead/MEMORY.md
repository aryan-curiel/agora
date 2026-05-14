# Memory — The Tech Lead

*Last updated: 2026-05-10*

## Stack Calibration Patterns

- **PoC platform default**: web prototype on Vercel, NOT mobile. React Native/Expo adds 2-3x build friction for a concept that hasn't validated user behavior yet. Mobile is MVP-phase at earliest.
- **Graph tech**: d3-force works for ≤100 nodes in browser. Beyond that, pre-compute layouts server-side or use static JSON. Never let force-simulation run client-side on large graphs.
- **AI latency**: Claude Haiku runs 2-5s per call. Always debounce + add loading states. Do not treat it as synchronous UX.

## Effort Estimate Calibrations

- **Graph-heavy PoCs**: 5-6 dev-weeks is realistic when graph data must be curated, a render pipeline built, and an AI integration added. 3-4 weeks is optimistic if any of those are unproven.
- **Data curation underestimated by non-technical agents**: "just use the dataset" ignores license checks, format normalization, and edge-case cleaning. Add 1-2 days minimum for any third-party dataset.

## External API / Dependency Gotchas

- **FlavorDB**: CC BY-NC 4.0 — blocks commercial use entirely. Do not propose as a data source for any monetized product.
- **USDA FoodData Central**: public domain, safe for commercial use. Lacks pairing data — must be manually curated or inferred.
- **Client-side JSON bundles**: 1K graph nodes ≈ 2-4MB. On 3G this is 8-15s load. Use paginated hydration: 60-node subgraph on first paint, lazy-load on tap. Add dimmed placeholder nodes with pulse animation.

## Recurring Hardest Technical Problems by Idea Type

- **Graph + discovery apps**: performance at scale (layout, bundle size, render). Always the first thing to prototype and stress-test.
- **AI-augmented apps**: latency management and graceful offline degradation. These are never "just call the API."

## Non-Technical Agent Assumptions That Were Wrong

- License-free ≠ commercially usable. Always verify specific license terms before committing a dataset to the stack.
- "Users will explore naturally" is not a cold-start solution — the UX must force a structured first path (e.g., 6 family tiles → 20-node subgraph → first value in <30s).
