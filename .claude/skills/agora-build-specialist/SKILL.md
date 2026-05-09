---
name: agora-build-specialist
description: Builds a new specialist agent from a job-post file. Conducts deep domain research, writes the specialist SKILL.md with research-grounded instructions, creates reference knowledge files for complex domains, registers the specialist in the roster, and marks the job-post as built.
version: 1.0.0
argument-hint: "[specialist-slug]"
allowed-tools: Read Write WebSearch WebFetch Bash
---

## Build a new specialist

### Setup

1. Resolve the specialist slug from $ARGUMENTS.
   If no argument provided, list all files in `job-posts/` with `status: draft`, show them, and ask the user to pick one.

2. Read `job-posts/specialist-{slug}.md` fully. Extract:
   - `name`, `status`, `date`, `requested-by`, `impact-rationale`, `reusability-rationale`
   - Role section, Knowledge Domain, Debate Behavior, Output Structure
   - Selection Criteria (include/exclude conditions)
   - Memory Update Mode patterns
   - Reference Specialists and boundaries
   - Example Round 1 Contribution

3. Abort if `status` is already `built`:
   Print: "specialist-{slug} has already been built. The skill exists at .claude/skills/specialist-{slug}/SKILL.md. To rebuild, manually reset status to 'draft' in the job-post."
   Stop.

4. Read every `.claude/skills/specialist-*/SKILL.md` to internalize the full existing roster:
   - Each specialist's identity, mandate, output structure
   - Boundary lines (what territory each already covers)
   This prevents the new specialist from duplicating existing coverage.

5. Read `.claude/skills/agora-lead-specialist/SKILL.md` to understand the current selection logic.

6. Confirm before building. Print:

   ── Build Preview ──────────────────────────────────────────
   Specialist: specialist-{slug}
   Role: {Role Name from job-post}
   Why hired: {impact-rationale}
   Reusability: {reusability-rationale}
   Domain: {Knowledge Domain summary, one line}

   This will:
   • Conduct web research on the {domain} domain
   • Write .claude/skills/specialist-{slug}/SKILL.md
   • Possibly write .claude/skills/specialist-{slug}/references/ files
   • Update agora-lead-specialist roster
   • Mark job-post as built

   Proceed? (y/n)
   ──────────────────────────────────────────────────────────

   If the user says no, stop.

### Research phase

7. Based on the job-post's Knowledge Domain, formulate **4 targeted search queries**:

   a. `"{domain} evaluation framework early-stage startup"` — to find structured evaluation criteria
   b. `"{domain} common failure modes product launch"` — to find failure patterns founders miss
   c. `"{domain} best practices PoC MVP [current year]"` — to find current practitioner standards
   d. `"{role} startup advisor checklist"` — to find practitioner heuristics from experts in this domain

   Where {domain} and {role} come from the job-post's Knowledge Domain and Role sections.

8. Execute all 4 web searches. From the results, select the 4-6 most credible and specific URLs:
   - Prefer: expert blogs, practitioner guides, academic frameworks, authoritative reference sites
   - Prefer: depth over breadth — choose pages that go deep on one framework over pages that skim many
   - Avoid: generic "Top 10 tips" listicles and paywalled content without previews

9. Fetch and read each selected URL. For each, extract:
   - **Named frameworks or methodologies** used by practitioners in this domain
   - **Specific evaluation criteria** that experts apply to early-stage products
   - **Common failure modes** — what goes wrong in this domain that founders overlook
   - **Key benchmarks or reference points** (numbers, percentages, timelines where applicable)
   - **The language and vocabulary** of domain experts (what do they actually call things?)

10. Synthesize the research into a working knowledge base — do not write files yet. Produce:

    **Findings:**
    - 4-8 named frameworks, tools, methodologies, or concepts specific to this domain
    - 3-5 failure modes most relevant to early-stage products
    - 2-4 specific things this specialist can name that other existing specialists would not
    - Cross-session memory patterns: what this specialist should accumulate across sessions

    **Reference file assessment** — decide YES or NO:
    - YES if: the domain has 3+ distinct evaluation frameworks or structured rubrics that would be too detailed to embed in a 400-word response but that the specialist should consult selectively
    - YES if: there are data tables, reference lists, or decision trees that are genuinely useful as lookup material
    - NO if: the research findings naturally distill into clear behavioral instructions that fit the SKILL.md
    - NO if: only 1-2 frameworks are relevant — embed them inline

    Record: `NEEDS_REFERENCES: yes|no` and if yes, plan file names and contents (max 2 files, max 250 lines each).

### Write the specialist SKILL.md

11. Write `.claude/skills/specialist-{slug}/SKILL.md` using this exact structure:

```
---
name: specialist-{slug}
description: {Role Name} specialist agent for Agora debate sessions. Invoked by agora-run-debate during active sessions.
user-invocable: false
context: fork
version: 1.0.0
---

You are the {Role Name} in a multi-agent idea development debate.
Your job: {one crisp sentence — the single mandate, derived from research and job-post}.

If `[YOUR MEMORY]` is provided in context, review it before responding — apply accumulated patterns about {2-3 specific cross-session pattern types relevant to this domain}.

{If NEEDS_REFERENCES is yes:}
If `[DOMAIN REFERENCES]` is provided in context, consult the relevant frameworks and benchmarks when forming your analysis.

Read the context provided. Then:

{3-5 concrete, sequential instructions. Each must:
 - Be specific and named (name actual frameworks, criteria, or concepts from research)
 - Tell the specialist WHAT to do, not just what to think about
 - Build toward a complete, useful contribution per round}

Rules:

{2-4 sharp rules. Minimum:
 - Be specific: name real [tools/frameworks/companies/numbers] — not vague generalities
 - The most useful rule drawn from research about what specialists in this domain get wrong
 - 250-400 words. No filler.}

## Memory update mode

When the context contains `MODE: memory-update`, ignore the debate instructions above.

You are given:
- `[CURRENT MEMORY]`: your existing memory file content (may be empty)
- `[YOUR CONTRIBUTIONS]`: your messages from this session, labeled by round
- `[SESSION SYNTHESIS]`: summary of what was established this session

Reflect on what is worth keeping long-term as the {Role Name}:
{3-4 specific reflection prompts derived from research findings — what patterns in THIS domain are worth accumulating}

Rules for memory:
- No idea-specific details — idea data lives in ideas/{slug}/
- Be concise: refine and compress existing entries rather than accumulating noise
- Merge new observations into existing memory; strengthen what proved true, revise what was contradicted
- Remove entries that are no longer accurate or useful

Return ONLY the full updated MEMORY.md content in this exact format:

# Memory — The {Role Name}

*Last updated: {YYYY-MM-DD}*

{your curated sections and entries — structure them however is most useful to your role}
```

Quality checks before writing:
- The specialist's core mandate is a single sentence with a clear verb ("ground", "surface", "define", "make real")
- Every instruction names something specific — no instruction says only "evaluate" or "consider" without naming what to look for
- The word "specific" or an equivalent constraint appears in the rules
- The memory reflection prompts are domain-specific, not generic
- The new specialist's instructions do not duplicate the mandate of any existing specialist

### Write reference files (if NEEDS_REFERENCES: yes)

12. For each planned reference file, write `.claude/skills/specialist-{slug}/references/{filename}.md`.

    Reference file format:
    ```markdown
    # {Descriptive Title} — {Role Name} Reference

    *Source: synthesized from domain research, {YYYY-MM-DD}*

    {Content — structured, scannable, practical. Tables, checklists, or named frameworks.
     No prose paragraphs — use headers, bullets, and tables.
     Each entry should be something the specialist can apply directly in a response.
     Max 250 lines.}
    ```

    Good reference file types:
    - Evaluation rubrics or scoring criteria
    - Named framework comparisons (e.g., "RICE vs. ICE vs. WSJF" with when to use each)
    - Domain-specific benchmark data (e.g., typical conversion rates, cost ranges, timelines)
    - Decision trees for common domain dilemmas

    Bad reference file types:
    - Generic "introduction to X" content
    - Content that repeats what's already in the SKILL.md
    - Content that requires frequent updates (news, pricing)

### Write changelog

13. Write `.claude/skills/specialist-{slug}/CHANGELOG.md`:

```markdown
# Changelog — specialist-{slug}

## [1.0.0] — {YYYY-MM-DD}

### Added
- Initial version: {1-2 sentences describing the specialist's role and what domain gap they fill}.
- Built from job-post: `{path to job-post file}`.
{If reference files: - Reference files: {list filenames} — {what they contain}.}

---
```

### Update run-debate to support domain references (first-time only)

14. Check if `.claude/skills/agora-run-debate/SKILL.md` already contains the text `DOMAIN REFERENCES`.
    - Use: `grep -c "DOMAIN REFERENCES" .claude/skills/agora-run-debate/SKILL.md`
    - If the count is 0, this is the first specialist with references — update run-debate step 8a.
    - If the count is > 0, skip this step (already patched).

15. If patching run-debate: in step 8a of agora-run-debate SKILL.md, after the block that reads MEMORY.md, insert:

```
   a2. Check if `.claude/skills/{specialist-name}/references/` exists:
       Use: `find .claude/skills/{specialist-name}/references -name "*.md" 2>/dev/null`
       If files exist, read all of them. Concatenate their content and pass it as [DOMAIN REFERENCES] in the context.
       If the folder does not exist or contains no .md files, omit [DOMAIN REFERENCES] from the context.
```

    Also add `[DOMAIN REFERENCES]: {content, if it exists}` to the context list in step 8b.
    Bump agora-run-debate's version by a patch (x.x.N+1) and add a CHANGELOG entry.

### Register the specialist

16. Update `.claude/skills/agora-lead-specialist/SKILL.md`:

    a. In the "Available specialists" section, add one line following the existing format:
       `- specialist-{slug}: {Role short description}. Include when {primary condition from job-post selection criteria}.`

    b. In the "Selection rules", add a numbered rule (before the roster size cap rule):
       Mirror the job-post's "Include when" conditions, condensed into one rule.

    c. Bump agora-lead-specialist's version by a minor bump (x.N+1.0) — this is a behavior change (new option in selection).
    d. Create or update `.claude/skills/agora-lead-specialist/CHANGELOG.md` with a minor entry.

### Mark the job-post as built

17. In `job-posts/specialist-{slug}.md` frontmatter, change:
    - `status: draft` → `status: built`
    - Add a new line: `built-date: {YYYY-MM-DD}` after the `status` line

### Print summary

18. Print:

    ══ Specialist Built ══════════════════════════════════════
    Specialist: specialist-{slug}
    Role: {Role Name}
    Version: 1.0.0

    Files written:
    • .claude/skills/specialist-{slug}/SKILL.md
    {• .claude/skills/specialist-{slug}/references/{file1}.md}
    {• .claude/skills/specialist-{slug}/references/{file2}.md}
    • .claude/skills/specialist-{slug}/CHANGELOG.md

    Registered in:
    • agora-lead-specialist v{old} → v{new} (minor)
    {• agora-run-debate v{old} → v{new} (patch) — added [DOMAIN REFERENCES] support}

    Job post: job-posts/specialist-{slug}.md → status: built

    Research grounding:
    • {n} web sources consulted
    • Key frameworks incorporated: {comma-separated list of named frameworks from research}
    {• Reference files: {n} files covering {brief description}}
    {• No reference files: domain knowledge embedded directly in instructions}

    To test: run /agora-run-debate {any-idea-slug} and verify specialist-{slug}
    is selected when its inclusion criteria are met.
    ════════════════════════════════════════════════════════
