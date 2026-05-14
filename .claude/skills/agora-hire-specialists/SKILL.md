---
name: agora-hire-specialists
description: Proposes new specialist agents to hire after a debate session, based on persistent gaps in coverage. Writes job-post files in job-posts/ for use by agora-build-specialist. Invoked automatically by agora-run-debate, and manually by the user after any session.
version: 1.0.0
argument-hint: "[idea-slug] [session-number]"
allowed-tools: Read Write Bash
author: Aryan Curiel
---

## Hire new specialists

### Setup

1. Resolve the session from $ARGUMENTS:
   - If `[idea-slug] [session-number]` provided, find `ideas/{slug}/sessions/{slug}-session-{n}-*.md`
   - If only slug provided, use the most recent session file in `ideas/{slug}/sessions/`
   - If no arguments, read `ideas_index.md` and ask the user to pick an idea and session

2. Read the session report fully. Extract:
   - **Synthesis** paragraph
   - **Open Questions** (unanswered after all rounds)
   - **Readiness breakdown** (before/after per dimension)
   - **Full transcript** (all specialist panels, all rounds)
   - **Specialists who participated** (from the "Specialists:" header line)

3. Read `ideas/{slug}/README.md`. Extract:
   - Idea description
   - Current open questions
   - Notes (if any)

4. Read `.claude/skills/agora-lead-specialist/SKILL.md` to get the full list of currently available specialists and their selection criteria.

5. Scan `job-posts/` for any existing draft job-posts (files matching `job-posts/specialist-*.md`).
   Note which specialist roles are already queued to avoid duplicates.

### Identify coverage gaps

6. For each open question in the session report, classify it by domain:
   - What kind of expertise would be needed to credibly answer it?
   - Is that domain already covered by a specialist who participated?
   - If covered: did that specialist actually address it, or did it remain open despite coverage?
   - If not covered: is there an existing specialist NOT in the roster who could have addressed it?

7. For each dimension that scored lowest (below 5/10 after the session), assess:
   - Why did it remain low? Was it lack of debate coverage, or genuinely hard to move?
   - Which domain of expertise is most relevant to that dimension?
   - Does that domain map to an existing specialist?

8. Review the transcript for moments where:
   - Specialists explicitly said "this needs someone with [X] expertise"
   - Questions were raised but dropped because no one had the knowledge to engage
   - A clear domain gap recurred across multiple rounds

9. Build a list of **candidate gaps**: specific expertise domains where dedicated coverage is absent and that absence had a measurable effect on the session.

### Apply the two mandatory filters

**Both filters must pass before a specialist can be proposed. Default to NOT proposing. A candidate that passes only one filter is NOT proposed.**

#### Filter 1 — Immediate session impact

For each candidate gap, assess: would a specialist with this expertise have materially changed the outcome of the next session on this idea?

Criteria for YES (all must be true):
- At least one open question directly maps to this domain
- The specialist's contribution would not merely restate what existing specialists already covered
- The dimension(s) relevant to this domain are still below 6/10

If the gap could be reasonably addressed by instructing an existing specialist to go deeper, or by adding a note to the idea, it does NOT pass this filter.

#### Filter 2 — Cross-idea reusability

For each candidate that passed Filter 1, assess: would this specialist provide meaningful value in sessions for other ideas (not just this one)?

Criteria for YES (all must be true):
- The domain need is structural, not specific to this idea's industry or context
- A conservative estimate is that >50% of future ideas in Agora would benefit from this specialist
- The expertise cannot be fully covered by combining prompts from two existing specialists

If the need is niche, highly context-dependent, or unlikely to recur across diverse idea types, it does NOT pass this filter.

### Decide: propose or skip

10. For each candidate gap:
    - If it passes both filters → write a job-post (step 11)
    - If it fails either filter → note why (for the summary) but do not write a job-post

    If no candidates pass both filters, skip step 11 entirely and print the summary (step 12) showing no hires recommended.

### Write job-post files

11. For each approved candidate, write `job-posts/specialist-{slug}.md`.
    Create the `job-posts/` directory if it does not exist.
    If a file already exists for this slug (including one found in step 5), overwrite it only if the new analysis justifies a materially different framing — otherwise skip and note the duplicate in the summary.

    Use this exact structure:

---
```
---
name: specialist-{slug}
status: draft
date: {YYYY-MM-DD}
requested-by: {path to session file}
impact-rationale: {1-sentence: what gap in THIS session this specialist would have filled}
reusability-rationale: {1-sentence: why other future ideas will also need this expertise}
---

# Job Post: {Human-Readable Role Name}

## Role

{1-2 sentences defining who this specialist is and their single core job in a debate session. Model on existing specialists: "You are the X in a multi-agent idea development debate. Your job: [one crisp sentence]."}

## Knowledge Domain

What this specialist must know deeply:
- {Specific framework, methodology, or domain knowledge — not vague}
- {A second area of deep expertise with named tools, concepts, or industries}
- {A third if applicable}

## Debate Behavior

How this specialist participates:
- **Stance**: {Their default posture — constructive critic, domain advocate, risk identifier, etc.}
- **Focus**: {What they look for that other specialists won't notice}
- **Interaction style**: {How they build on or challenge what others say}
- **What they must not do**: {Overlap to guard against — what existing specialists already handle}

## Output Structure

Each round, produce:
1. {First element — e.g., "Identify 2 critical gaps in the [domain] plan"}
2. {Second element — e.g., "Give concrete recommendations with named examples (tools, vendors, frameworks)"}
3. {Third element if applicable}
4. End with exactly 2 actionable questions the team must answer before proceeding in this domain.

Word count: 250–400 words. No filler.

## Selection Criteria

Include in sessions when:
- {Specific readiness condition, e.g., "dimension_X < 6"}
- {Idea type condition, e.g., "idea involves [X type of domain or product]"}
- {Optional: "Always include when [high-stakes condition]"}

Exclude when:
- {When this specialist adds no value — e.g., "OSS tools with no operational surface area"}

## Memory Update Mode

After each session, reflect on and retain:
- {What types of patterns are worth accumulating, e.g., "Which [domain] failure modes recur across ideas"}
- {What recommendations proved accurate or inaccurate}
- {What questions most effectively surfaced real problems}

## Reference Specialists

Most similar to:
- **{existing-specialist}**: {How this new one differs — what distinct territory it covers}

Must not duplicate:
- **{existing-specialist}**: {The boundary — what territory to leave to them}

## Example Round 1 Contribution

> {A realistic 4-6 sentence example of what this specialist would say in round 1 of a typical session. Write in first person, in the specialist's voice. Show specificity — name real things: tools, failure modes, frameworks, numbers. Demonstrate what they uniquely add that existing specialists would not say.}
```
---

### Print summary

12. Print:

    ── Specialist Hiring Review ───────────────────────────────
    Session: {filename}
    Candidates evaluated: {n}

    Hired — Job posts written:
    {for each proposed specialist:
    • specialist-{slug}
      Impact:       {impact-rationale}
      Reusability:  {reusability-rationale}
      File: job-posts/specialist-{slug}.md
      Next step: /agora-build-specialist specialist-{slug}}

    Not hired — filtered out:
    {for each rejected candidate:
    • {domain}: {one-line reason — which filter failed and why}
      (e.g., "Operations/DevOps: Filter 2 failed — relevant only to SaaS infra ideas, not broadly reusable")}

    {if no candidates were proposed:}
    No new specialists recommended. Existing roster adequately covers the gaps in this session.

    ──────────────────────────────────────────────────────────
    To build a specialist from a job post: /agora-build-specialist {slug}
    ──────────────────────────────────────────────────────────
