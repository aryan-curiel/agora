---
name: show-idea
description: Show the full details of a specific idea including readiness breakdown, open questions, and session history. Use when the user wants to inspect, review, or get details about a specific idea.
argument-hint: "[idea-id or idea name]"
version: 1.0.0
---

## Show idea details

1. Resolve the idea from $ARGUMENTS:
   - If it looks like a slug (lowercase, hyphens), read ideas/{slug}/README.md directly
   - If it looks like a name, search ideas_index.md for a match and resolve to slug
   - If ambiguous, list matches and ask the user to confirm
2. Read the full idea file.
3. Display:
   - Name, ID, status, description
   - Readiness score with full breakdown table and progress bars per dimension
   - Open questions (numbered list)
   - Current best answers
   - Session history table
   - Suggested next action based on lowest-scoring dimensions
4. If no sessions yet, suggest: "No sessions yet. Run /run-debate to start developing this idea."
