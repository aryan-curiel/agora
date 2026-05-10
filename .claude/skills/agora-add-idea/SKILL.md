---
name: agora-add-idea
description: Add a new idea to Agora. Use when the user wants to add, create, or record a new idea, project, app, business concept, or anything they want to develop.
disable-model-invocation: true
argument-hint: "[idea name]"
version: 1.1.0
---

## Add a new idea

1. If $ARGUMENTS is empty, ask the user for the idea name. Otherwise use $ARGUMENTS as the name.

2. **Step 2a — Brief description.** Ask: *"Describe the idea in a sentence or two — what is it?"* Wait for the answer. Use this as the `## Description` field in the README.

3. **Step 2b — Targeted clarifying questions.** Send this exact follow-up in one message (do not split into separate prompts):

   > Great. To give the first draft as much detail as possible, answer any of these you already know — skip the rest, and even rough notes help:
   >
   > 1. **Problem & users** — Who specifically has this problem, and what does it cost them today?
   > 2. **Core features** — What are the 3–5 must-have features for a first version?
   > 3. **Tech stack** — Any stack preferences, constraints, or existing infrastructure to work with?
   > 4. **Go-to-market** — How will you get your first 10 users or customers?
   > 5. **Key risks** — What's most likely to kill this idea?
   > 6. **PoC scope** — What's the smallest thing you could build to prove the core concept works?
   > 7. **Success metrics** — How will you know after 90 days if it's working?
   > 8. **Monetization** — Personal/OSS project, or do you have a revenue model in mind?
   > 9. **Budget / effort** — Any budget ceiling or time constraint you're working within?

   Wait for the user's reply. Note which questions they answered and which they skipped.

4. Generate a slug: lowercase, hyphen-separated, max 40 chars. Example: "AI Recipe App" → "ai-recipe-app"

5. Check that ideas/{slug}/README.md does not already exist. If it does, tell the user and ask if they want to update it instead.

6. Create the directory ideas/{slug}/sessions/ and write ideas/{slug}/README.md using the standard idea file format from CLAUDE.md, incorporating all gathered answers:

   - **Description** — use the brief description from step 2a.
   - **Constraints** — include an empty `## Constraints` section between `## Status` and `## Readiness Score`:
     ```
     ## Constraints

     | Constraint | Rationale |
     |---|---|
     ```
     (Leave the table with no data rows — constraints are added later via /agora-add-constraint.)
   - **Readiness breakdown** — for each of the 10 dimensions:
     - If the user answered the corresponding question: assign an initial score of 3–6/10 (higher if the answer is specific and detailed, lower if vague) and write a note summarising their answer.
     - If the user skipped it: score 0/10, note "Not yet assessed."
   - **Readiness Score** — calculate the overall percentage from the breakdown scores (sum of scores / 100, since max is 10×10).
   - **Current Best Answers** — one sub-heading per dimension the user answered, with their answer verbatim or lightly reformatted for clarity. Omit dimensions they skipped.
   - **Open Questions** — list only the dimensions the user did *not* answer (e.g. "What is the go-to-market strategy?"). If the user answered everything, write "None — all dimensions have initial answers."

7. Add a row to ideas_index.md with the calculated readiness score, status active, sessions 0, today's date.

8. Confirm creation with a summary:
   - ID: {slug}
   - File: ideas/{slug}/README.md
   - Initial readiness: {score}% across {n} answered dimensions
   - Next step: run /agora-run-debate to start developing it
