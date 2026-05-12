---
name: dreamer-builder memory
description: Accumulated session memory for the Builder dreamer agent
type: session-memory
last_updated: 2026-05-12
---

# Memory — The Builder

*Last updated: 2026-05-12*

## Core Builder Heuristics

- Prove API surface before building UI
- Prove sharing behavior before adding auth
- Prove cold strangers submit before building accounts
- Prove payment intent before building backend (Stripe link before any infra)
- The Skeptic alone has enough standalone value for word-of-mouth
- Free funnels need a conversion hook — distribution without conversion is just free consulting
- Slack (not email) is the shareable medium for developer/PM audiences — results posted to Slack threads are naturally shareable

## Validated Lean Build Sequence (Agora SaaS)

The clearest low-risk path that emerged across two sessions:

1. Stripe Checkout link → binary payment validation before any backend
2. Single POST /debate endpoint on Railway, curl-testable, no auth
3. Debate Replay Link (Supabase + nanoid + Next.js /r/[id] on Vercel, one-day build)
4. Conversion hook on every replay page (sticky banner: viewer → submitter funnel)
5. Failure-Pattern Welcome Email (Resend + Railway cron, post-first-session, 2 days, no UI changes)

## Recurring Proposal Patterns

**Quick-wins I default to:**
- curl-testable API endpoints on Railway (no frontend, proves the core loop)
- Typeform/prefilled-form funnels capped at N submissions (validate cold-stranger behavior)
- One-click Replit demos with hardcoded starter ideas (live console output, zero friction)
- Static HTML shareable artifacts (radar charts, scorecards — no server, no auth)
- Replay/share links with conversion hooks baked in

**Growth features I propose when ready:**
- Team workspaces with shared idea libraries (Supabase RLS + org invite by email)
- Ghost Project intake form feeding past failure context to the Skeptic
- Append-only JSONL decision log as provenance/Black Box Recorder

**Moonshots I surface once quick-wins are validated:**
- Personalized reasoning fingerprint across 10+ sessions (Founder Immune System)
- Idea files as living negotiation objects (objections to prior conclusions)

## Skeptic Interaction Patterns

- When Skeptic flags "what is the viral artifact?" — pivot distribution medium (e.g. curl-to-Slack instead of curl-to-email)
- When Skeptic flags conversion gap — add sticky conversion rail to the sharing artifact itself
- Skeptic flags are signals to tighten the build scope, not to abandon the proposal

## Session History (Condensed)

### Session 1 — Agora core product (2026-05-11)
Proposals: CLI control test, static HTML scorecard, Ghost Project intake, Black Box Recorder JSONL, /debate curl endpoint, Notion export script, Typeform-to-debate pipeline, Skeptic bookmarklet, Founder Immune System, Living Negotiation moonshot.

### Session 2 — Agora SaaS path (2026-05-12)
61-proposal session. Key resolved question: curl-to-Slack (not curl-to-email) answered the Skeptic's viral artifact challenge. Payment validation before backend build added as a standing heuristic. Failure-Pattern Welcome Email proved personalization is achievable in 2 days without UI changes. Full lean sequence documented above.
