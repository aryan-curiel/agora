---
name: agora-list-ideas
description: List all ideas with their readiness scores and status. Use when the user asks to see their ideas, check progress, or wants an overview of what they are working on.
argument-hint: "[filter: active|completed|all]"
version: 1.0.0
author: Aryan Curiel
---

## List ideas

1. Read ideas_index.md
2. If $ARGUMENTS specifies a filter (active, completed, all), apply it. Default is active.
3. For each idea in the index, read ideas/{slug}/README.md to get current score and open questions count.
4. Display a formatted table:

   ID | Name | Score | Progress Bar | Sessions | Open Questions
   ---|------|-------|--------------|----------|---------------

   Progress bar: use █ for filled (each █ = 10%), ░ for empty. Example: 34% = ███░░░░░░░ 34%
   Color coding in output: <40% show as low, 40-70% medium, >70% high readiness.

5. Show total count and average readiness at the bottom.
6. Suggest next action: "Run /agora-run-debate [idea-id] to start a session on your lowest-scoring idea."
