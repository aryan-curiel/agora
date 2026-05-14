# Memory — The Legal Advisor

*Last updated: 2026-05-11*

## Copyright & Content Licensing

- **Cookbooks and culinary reference works** (e.g., The Flavour Thesaurus by Niki Segnit, published by Bloomsbury) are copyrighted expression — flavor pairing descriptions, prose, and curated combinations cannot be digitized or redistributed without a license. Hard launch blocker, not a scale-time concern.
- **Hard blockers vs. scale-time**: Copyright infringement on a named third-party work = hard blocker. GDPR opt-in gaps, ToS ambiguity on free-tier APIs = scale-time. Keep this distinction sharp.
- **Recommended pattern for PoC**: Use open/CC-licensed datasets (e.g., FlavorDB CC BY-NC 4.0) as placeholders while pursuing licensing. Preserves buildability without legal exposure.
- **CC BY-NC 4.0 datasets**: Legally safe for non-commercial PoC and closed beta. Commercial launch requires re-evaluation. Critical implementation constraint: CC BY-NC data cannot appear in any paid-tier output chain. Enforce at the API layer — two separate endpoints (non-commercial exploration vs. commercially clean generation from ingredient names only).
- **Flavornet (Ahn et al., 2011, Cornell/Notre Dame)**: Open-access academic data on aroma compound co-occurrence, ~1,000 ingredients. No formal license attached (pre-dates common open-data licensing). Safe use pattern: cite the paper, do not claim the data as proprietary, do not resell the raw data. Building a derived graph product is academically standard practice. To be fully safe: email the corresponding author (Barabási lab, Notre Dame) for written confirmation before committing as a fallback data source. One email, one week turnaround.
- **Publisher licensing fees**: Culinary publishers (Bloomsbury-type) typically charge £2,000–10,000/year flat fee OR 3–8% royalty on gross revenue for digital product licenses. Always get a written fee estimate before MVP build — this number materially affects the budget ceiling.

## Data Privacy

- **Push notifications** require Article 7 GDPR opt-in consent (explicit, granular, revocable). Recurring requirement for any app with notification features targeting EU users.
- **Location data** infers personal data under GDPR and may touch Article 9 (sensitive data categories) depending on use. Default to manual region/country selection rather than GPS — avoids Article 9 surface entirely at PoC stage.
- **EU users at beta stage**: Gate beta sign-up with a region selector and block EU sign-ups until a proper GDPR consent flow is implemented. Easier to enforce at launch than to retrofit consent post-launch.

## Minimum Viable Privacy Policy

A closed beta in an English-speaking market with no EU targeting can launch with a one-page policy. Must cover:
1. Data collected (email if notification opt-in, anonymous usage analytics, WTP survey response — no payment taken)
2. How data is used (product improvement only, not sold, not shared)
3. Deletion (email "delete my data" to [address] = deletion within 7 days)
4. EU users: explicit statement that EU sign-ups require a separate consent flow

Write this before the FIRST tester session, not before public launch. Testers are users and are covered by the policy from session one.

## Platform & API ToS

- Features that derive content from a licensed third-party dataset (even indirectly, e.g., "trending combinations" seeded from Thesaurus-derived pairings) compound copyright exposure. Chain-of-custody matters — the origin of data used in ML or aggregation features must be clean.
- **CC BY-NC API-layer enforcement**: Do not enforce CC BY-NC restrictions at application logic level. Enforce at the API layer: two separate endpoints with distinct data access policies. Non-commercial exploration endpoint uses FlavorDB. Paid recipe generation endpoint receives only ingredient names (factual, not copyrightable) — the LLM's own knowledge generates the rest. One day of implementation; resolves the commercial licensing gap completely.

## Founding Member / Early Access Schemes

- Non-financial founding member schemes (no equity, no revenue share, no perpetual discounts) are low risk. Financial components (even informal) trigger securities or consumer protection considerations — flag immediately if introduced.

## Pre-Beta Legal Checklist

Before first tester session (one working day):
1. ☐ Privacy policy written and linked on landing page
2. ☐ Data source confirmed (Bloomsbury inquiry sent, or Flavornet + editorial confirmed as fallback)
3. ☐ Flavornet author email sent for usage confirmation (if using as fallback)
4. ☐ API endpoints separated: CC BY-NC data in non-commercial endpoint only; paid endpoint receives ingredient names only
5. ☐ EU sign-up gate implemented (region selector, block EU until GDPR consent flow)
6. ☐ Founding member scheme documented as non-financial only

## General PoC Stance

- Most PoCs in consumer food/lifestyle have zero hard legal blockers for closed beta. The bar for a hard blocker is: named IP infringement, regulated industry data (health records, financial transactions), or children's data (COPPA). Absent these, default to "get a lawyer before public launch, not before beta."
- Exception: if the core dataset is a copyrighted commercial work (e.g., Flavour Thesaurus), the copyright question must be resolved or the fallback data strategy must be confirmed before ANY code using that data is written.
