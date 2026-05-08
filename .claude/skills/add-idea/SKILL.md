---
name: add-idea
description: Add a new idea to Agora. Use when the user wants to add, create, or record a new idea, project, app, business concept, or anything they want to develop.
disable-model-invocation: true
argument-hint: "[idea name]"
version: 1.0.0
---

## Add a new idea

1. If $ARGUMENTS is empty, ask the user for the idea name. Otherwise use $ARGUMENTS as the name.
2. Ask the user to describe the idea in as much detail as they have right now. Tell them the more they share, the better the first debate session will be.
3. Generate a slug: lowercase, hyphen-separated, max 40 chars. Example: "AI Recipe App" → "ai-recipe-app"
4. Check that ideas/{slug}/README.md does not already exist. If it does, tell the user and ask if they want to update it instead.
5. Create the directory ideas/{slug}/sessions/ and write ideas/{slug}/README.md using the standard idea file format from CLAUDE.md.
6. Add a row to ideas_index.md with score 0%, status active, sessions 0, today's date.
7. Confirm creation with a summary:
   - ID: {slug}
   - File: ideas/{slug}/README.md
   - Next step: run /run-debate to start developing it
