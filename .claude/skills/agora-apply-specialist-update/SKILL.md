---
name: agora-apply-specialist-update
description: Applies a pending proposal to upgrade a skill definition, bumps its version, cascades updates to agents affected by breaking changes, marks the proposal as applied, and records the change in each agent's CHANGELOG.md.
version: 1.1.0
argument-hint: "[specialist-name] [version]"
allowed-tools: Read Write
author: Aryan Curiel
---

## Apply a specialist update

### Locate the proposal

1. Resolve the specialist name from $ARGUMENTS (first token).
   If missing, scan all `.claude/agents/*/PROPOSAL-*.md` files for those with `status: pending`,
   list them, and ask the user which specialist to update.

2. If a version is provided as the second token, read `.claude/agents/{specialist-name}/PROPOSAL-v{version}.md`.
   Otherwise, list all `PROPOSAL-*.md` files in the specialist's agent folder whose frontmatter has `status: pending`.
   - If exactly one pending proposal exists, use it automatically.
   - If multiple pending proposals exist, show them and ask the user which to apply.

3. Read the full proposal. Extract: specialist, current-version, proposed-version, change-type, breaking (yes/no), affected-specialists, and all proposed changes.

### Validate

4. Read `.claude/agents/{specialist-name}.md`. Check that the `version` field in its frontmatter matches the proposal's `current-version`.
   - If they match, proceed.
   - If they don't match, warn: "The skill's current version is {actual} but this proposal was written for {expected}. The proposal may be stale or already partially applied. Continue? (y/n)"
   - If the user declines, stop.

### Consult architecture guidance for major changes

4b. If `change-type` is `major`:
   a. Check whether the proposal contains an "Architectural Notes" section recommending architecture review.
   b. Ask: "This is a major structural change. Would you like to validate the new design with /knowledge-architect before applying? (y/n)"
   c. If yes: pause and instruct the user to run `/knowledge-architect` with the proposed changes as input, then return here once validated.
   d. If no: proceed to step 5.

### Apply changes to the target agent

5. For each "Proposed Skill Changes" section in the proposal:
   a. Locate the exact "Current instruction" text block inside the SKILL.md body.
   b. Replace it with the "Proposed instruction" text.
   c. If the exact text cannot be found, show both texts and the diff, then ask:
      "Could not find the exact current text in {specialist-name}/SKILL.md. Apply manually? Paste the section to replace, or skip this change."

6. Update the `version` field in the SKILL.md frontmatter to the `proposed-version`.
   If no `version` field exists in the frontmatter, add it as the last field before the closing `---`.

### Handle breaking changes

7. If the proposal has `Breaking: yes` and lists affected specialists:
   a. For each affected specialist, read their SKILL.md and identify what needs to change due to the format or interface change.
   b. Describe the required change clearly: "Specialist {name} calls {target specialist} and expects {old format}. It needs to be updated to expect {new format}."
   c. Ask: "Specialist {name} needs a cascade update. Apply it automatically? (y/n)"
   d. If yes:
      - Apply the mechanical change to the affected agent's SKILL.md
      - Bump its PATCH version
      - Update its CHANGELOG.md with a new patch entry noting the cascade reason
   e. If no, note it in the summary output so the user can handle it manually.

### Mark the proposal as applied

8. Edit the proposal file's frontmatter:
   - Change `status: pending` to `status: applied`
   - Add a new line `applied-date: {YYYY-MM-DD}` after the `status` line

### Update the target agent's CHANGELOG

9. If `.claude/agents/{specialist-name}/CHANGELOG.md` does not exist, create it with:
   ```
   # Changelog — {specialist-name}
   ```

10. Prepend a new version entry to the CHANGELOG (after the `# Changelog` header, before any existing entries):

## [{proposed-version}] — {YYYY-MM-DD}

### {Changed|Added|Fixed}
{One bullet per applied change, written in past tense describing the new behavior.
 Example: "Added explicit instruction to name specific subreddits when proposing distribution channels."}

**Source:** Proposal `PROPOSAL-v{proposed-version}.md` — session `{session path from proposal}`

---

### Print summary

11. Print:

    ══ Specialist Updated ════════════════════════════════════
    Specialist: {specialist-name}
    Version:    {current} → {proposed} ({change-type})
    Proposal:   PROPOSAL-v{proposed}.md → status: applied
    Changelog:  CHANGELOG.md updated

    {If cascade updates were applied:}
    Cascade updates applied:
    • {affected-specialist}: {old} → {new} (patch) — CHANGELOG updated

    {If cascade updates were declined:}
    Manual updates needed:
    • {affected-specialist}: {description of what needs to change}

    Run /agora-review-specialists {slug} after the next session to continue improving specialists.
    ════════════════════════════════════════════════════
