---
name: agora-add-note
description: Add a note to a specific idea. Notes are lightweight observations, feature ideas, considerations, proposals, or risks that should be captured without triggering a debate session.
argument-hint: "[idea-id]"
version: 1.0.0
author: Aryan Curiel
---

## Add a note to an idea

1. Resolve the idea from $ARGUMENTS:
   - If it looks like a slug (lowercase, hyphens), check that ideas/{slug}/README.md exists
   - If it looks like a name, search ideas_index.md for a match and resolve to slug
   - If $ARGUMENTS is empty or ambiguous, list active ideas and ask the user to pick one

2. Ask the user for the note type if not clear from context. Options:
   - **feature** — a capability worth adding or exploring
   - **consideration** — something to keep in mind, a constraint or nuance
   - **proposal** — a concrete change or direction to evaluate
   - **observation** — something noticed about the market, users, or problem space
   - **risk** — a potential failure mode not yet captured in Key Risks

3. Ask the user for the note text if not already provided. Keep it concise (1–3 sentences).

4. Read ideas/{slug}/README.md.

5. If a `## Notes` section exists, append a new row to its table. If it does not exist, add it after the `## Open Questions` section using this format:

   ```
   ## Notes

   | Date | Type | Note |
   |---|---|---|
   | {today} | {type} | {note text} |
   ```

6. Write the updated file.

7. Confirm with:
   - Idea: {name}
   - Type: {type}
   - Note saved: {note text truncated to 80 chars}
   - Tip: "Notes are surfaced during debate sessions. Run /agora-show-idea {slug} to review all notes."
