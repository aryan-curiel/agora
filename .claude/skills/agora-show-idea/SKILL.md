---
name: agora-show-idea
description: Show the full details of a specific idea including readiness breakdown, constraints, notes, proposals from brainstorm sessions, open questions, and session history. Use when the user wants to inspect, review, or get details about a specific idea.
argument-hint: "[idea-id or idea name]"
version: 1.1.0
---

## Show idea details

1. Resolve the idea from $ARGUMENTS:
   - If it looks like a slug (lowercase, hyphens), read ideas/{slug}/README.md directly
   - If it looks like a name, search ideas_index.md for a match and resolve to slug
   - If ambiguous, list matches and ask the user to confirm
2. Read the full idea file.
3. Display in this order:

   **Header**
   - Name, ID, status (with emoji: 🟢 active / 🔵 parked / ✅ done / ⬜ draft), and description

   **Constraints** (if any rows exist in the Constraints table)
   - Show as a table with constraint and rationale columns
   - If no constraints: omit this section entirely

   **Readiness**
   - Overall readiness score as a visual progress bar (e.g. `████████░░ 80%`)
   - Full breakdown table with per-dimension score and notes
   - Highlight the 3 lowest-scoring dimensions as "Focus areas"

   **Open Questions**
   - Numbered list

   **Current Best Answers**
   - As-is from the file

   **Notes** (if any rows exist)
   - Table with date, type, and note text
   - Append: "Notes will be surfaced to agents in the next session."

   **Proposals** (if the Proposals section exists and has content)
   - Show the last-updated line
   - List all Quick Wins as a bulleted list (include session tag)
   - List Growth Features and Moonshots as collapsed counts: "X growth features, Y moonshots — run /agora-show-idea {slug} --full to expand" (if terminal doesn't support collapse, show them anyway)
   - If no proposals yet: omit this section

   **Session History**
   - Table with session #, type, date, rounds, proposals, and report link

4. Suggested next action:
   - If no sessions yet: "No sessions yet. Run `/agora-run-debate` or `/agora-brainstorm` to start."
   - Else: suggest the skill most appropriate for the lowest-scoring dimensions (debate for scoring, brainstorm for early ideation).
