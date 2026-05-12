---
name: agora-list-proposals
description: Lists all pending specialist improvement proposals ordered by potential impact, and calls out which ones are highly recommended to apply. Use when the user wants to see what proposals are waiting or decide what to apply next.
version: 1.0.0
argument-hint: ""
allowed-tools: Read Bash
author: Aryan Curiel
---

## List pending proposals

### Collect proposals

1. Scan every directory under `.claude/skills/` for files matching `PROPOSAL-v*.md`.
   Use: `find .claude/skills -name "PROPOSAL-v*.md"`

2. For each file found, read it and extract from the frontmatter:
   - `specialist` — name of the specialist
   - `current-version` — version before the change
   - `proposed-version` — version after the change
   - `change-type` — patch | minor | major
   - `session` — path to the session that triggered the review
   - `date` — date the proposal was written
   - `status` — skip any file where status is not `pending`

   From the body, extract:
   - Observed issues list: count total issues; count how many are tagged `[major]`, `[moderate]`, `[minor]`
   - Breaking Change Analysis: `Breaking: yes/no` and `Affected specialists` list (count them)
   - Summary sentence (first sentence under `### Summary`)

3. If no pending proposals are found, print:
   ```
   ── Pending Proposals ──────────────────────────────────────
   No pending proposals found. Run /agora-review-specialists after a session to generate proposals.
   ──────────────────────────────────────────────────────────
   ```
   and stop.

### Score each proposal for impact

4. Compute an **impact score** (0–10) for each pending proposal:

   | Factor | Points |
   |--------|--------|
   | change-type: patch | +1 |
   | change-type: minor | +2 |
   | change-type: major | +4 |
   | Breaking: yes | +2 |
   | Each affected downstream specialist (max 3) | +1 each |
   | Each `[major]` observed issue (max 2) | +1 each |
   | Each `[moderate]` observed issue (max 1) | +0.5 |
   | Proposal date is 14+ days old (stale) | +0.5 |

   Cap the total at 10.

### Classify each proposal

5. Assign a tier based on impact score:
   - **Highly Recommended** — score ≥ 5, OR change-type is `major`, OR breaking is `yes`
   - **Recommended** — score ≥ 3 and not in Highly Recommended
   - **Optional** — everything else

### Print output

6. Print the full list, sorted by impact score descending within each tier:

```
── Pending Proposals ──────────────────────────────────────
Found {n} pending proposal(s) across {m} specialist(s)

⭐ Highly Recommended
─────────────────────
{rank}. {specialist-name}  v{current} → v{proposed}  [{change-type}{" · breaking" if breaking}]
   Impact: {score}/10  |  Issues: {total} ({major_count} major, {moderate_count} moderate, {minor_count} minor)
   Affected specialists: {list or "none"}
   Session: {session path}
   Date: {date}{" ⚠ stale" if 14+ days old}
   Summary: {one-sentence summary}

   → /agora-apply-specialist-update {specialist-name}

{repeat for each in tier}

Recommended
───────────
{same format}

Optional
────────
{same format}

──────────────────────────────────────────────────────────
To apply: /agora-apply-specialist-update {specialist-name}
To review a new session: /agora-review-specialists {slug}
──────────────────────────────────────────────────────────
```

   Omit a tier section entirely if it has no proposals.
   If a proposal file lacks a `Breaking` field, treat it as `Breaking: no`.
