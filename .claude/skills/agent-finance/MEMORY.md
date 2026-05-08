# Memory — The Finance Specialist

*Last updated: 2026-05-08*

## Forgotten Cost Categories

**Landing page / design tooling**
Consistently omitted from MVP budgets. Budget $50–100 for Framer, Webflow, or similar. Founders think "I'll just use Tailwind" and then spend 20 hours on it.

**API cost pass-through at free tier**
Free tiers with any LLM call create a silent cash drain. At $1/session and 500 free users × 3 sessions = $1,500 before first dollar of revenue. Always model free-tier cost at 10x expected usage before setting free limits.

**Stripe fees on small ticket prices**
2.9% + $0.30 eats 5–8% of revenue at $10–15/month price points. Include in unit economics from day one.

## Pricing Model Failure Modes

**"Unlimited" on API-cost-per-use products**
Unlimited sessions/requests on any product with a per-use API cost will create negative-margin power users who are also your most vocal advocates. Always cap or introduce overage pricing. Example: Builder tier at $29/unlimited breaks when power users run 20+ sessions at $1.20/session each.

**Session-cap tiers with near-zero margin**
A $12/month tier with 8 sessions at $1.20/session API cost leaves ~$2.40 gross margin (20%) before infra. The fix is either raise price to $19+ or reduce cap to 5 sessions. Target ≥50% gross margin on all paid tiers.

**"Free to self-host, pay for hosted" OSS + SaaS models**
This structure works well when the self-host option is genuinely non-trivial (requires technical setup). If the OSS version is too easy to run, the hosted tier loses its value. Ensure the hosted tier adds clear value beyond ease-of-setup (persistent storage, team features, managed API keys).

## Phase Budget Calibration

**PoC:** $0–50 is accurate for Claude Code native projects with no infra. API costs are the only real spend. Instrument actual token cost per session before setting pricing.

**MVP:** $600–900 one-time for solo founder with dev skills. Breakdown: Vercel + Supabase + Clerk + Stripe setup + domain + landing page. Monthly recurring: $45–80 at zero revenue. This estimate is consistently under-stated by founders who forget the landing page and Clerk paid tier trigger.

**V1 ($1K MRR):** Requires ~53 Solo subscribers at $19/mo or 26 Builder at $39/mo. At 2–3% free-to-paid conversion, need 1,750–2,600 free signups minimum. Organic IH/HN/PH launch can deliver 500–2,000 signups in first 30 days if the product has genuine shareability.

## Financial Risk Patterns

**API cost drift as product grows**
Per-session cost grows with context window (longer memories, more agents, more rounds). What costs $0.40/session at launch may cost $2.50/session 6 months later. Enforce hard token budgets at the orchestration layer before growth, not after a surprise bill.

**CAC unknowns before paid acquisition**
Always budget $200–500 for a controlled paid acquisition test (Reddit Ads, newsletter sponsorship) before assuming organic-only will reach the conversion target. Organic distribution is real but slow; CAC validation unlocks the decision to invest in paid.

**Revenue timeline realism**
$1K MRR in 3–6 months post-launch is achievable only with a successful PH launch and sustained IH/community distribution. Without a viral or paid channel, organic compound growth typically delivers $1K MRR in 9–12 months for a solo founder.
