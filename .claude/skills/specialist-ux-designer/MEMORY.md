# Memory — The UX Designer

*Last updated: 2026-05-10*

## Core PoC Journey Patterns

**Graph/discovery products**: Entry point must be a single concrete action (pick one thing), not an open canvas. Constrain visible node count (20 nodes, 3 affinity colors). The journey is: anchor → expand → select → output. Four screens maximum.

**Onboarding is almost always wrong for PoC.** Drop it. Get to the core loop in under 60 seconds. First-session value must arrive before any account or preference collection.

**Second-session re-entry** needs a single trigger: show last saved item + one "explore something new" suggestion tile from a different family. One tap sets the new root. Do not build a dashboard or history list for PoC.

## Moment of Value Patterns

- For discovery tools: moment of value = first unexpected-but-correct suggestion the user didn't think of themselves. Design to reach that moment in under 60 seconds.
- What slows it down: onboarding flows, account gates, browse/explore modes that delay the core action.

## Scope Cuts That Repeatedly Proved Correct

- **Browse/explore mode**: users anchor on search, not browsing. Cut it.
- **Full recipe generation**: a recipe card (dish name + 5 ingredients + 3-step method) is sufficient.
- **User accounts**: local storage handles PoC retention. Accounts are infrastructure, not value.
- **Multi-ingredient input**: single-ingredient anchor only until core loop is validated.
- **User-generated ratings**: gate to returning users post-cook only. 2-tap max (Worked/Didn't). No free text. MVP+, not PoC.

## Pre-Build Validation Protocol

No-code test before writing code: static mockup (30 circles, SVG lines, no color, no interaction), single instruction ("Plan a dish using this map"), observe 8 minutes, pass threshold = 6/10 users trace coherent paths. Catches graph legibility and navigation assumptions before any engineering investment.

## Retention Micro-Feature Rule

One optional low-friction context capture is acceptable: e.g., 10-word "What are you making?" on save. Validate by usage rate (>50% saves include it, or cut it).

## Rendering / Loading Patterns

- Lazy-load boundaries must show dimmed placeholder nodes with pulse animation, not blank space. Blank space reads as broken.
- Constrain initial graph load to ~60 nodes; lazy-load neighbors on tap.

## Wrong Assumptions from Other Agents

- Assuming users will explore freely in graph interfaces — they anchor on familiar nodes. Color coding and affinity grouping are navigational aids, not decorative.
- Assuming retention requires accounts — local storage is sufficient to test whether users return at all.
