---
name: agora-add-constraint
description: Add a hard constraint to a specific idea. Constraints are enforced during all debate sessions — specialists must respect them and may only propose overriding them with an explicit marker and strong justification.
argument-hint: "[idea-slug] [constraint text]"
allowed-tools: Read Write
version: 1.0.0
author: Aryan Curiel
---

## Add a constraint to an idea

1. Resolve the idea slug from $ARGUMENTS (first token).
   If no slug provided, read `ideas_index.md` and ask the user to pick an idea.

2. Read `ideas/{slug}/README.md` fully.

3. Determine the constraint and rationale:
   - If the remaining tokens in $ARGUMENTS provide a constraint, use that as the constraint text.
   - Ask the user for the rationale (why this constraint exists) unless they already provided it.
   - If no constraint text was provided at all, ask: "What is the constraint? (e.g. 'Must use React + TypeScript', 'PoC budget ≤ $500')"

4. Locate the `## Constraints` section in the idea file:
   - If the section exists, append a new row to its table:
     `| {constraint} | {rationale} |`
   - If the section does not exist, insert it between `## Status` and `## Readiness Score`:
     ```
     ## Constraints

     | Constraint | Rationale |
     |---|---|
     | {constraint} | {rationale} |
     ```

5. Write the updated file.

6. Confirm:

   ── Constraint Added ──────────────────────────────
   Idea: {name} ({slug})
   Constraint: {constraint}
   Rationale: {rationale}

   Specialists will respect this constraint in all future debate sessions.
   To add another: /agora-add-constraint {slug}
   ──────────────────────────────────────────────────
