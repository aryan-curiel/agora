# Skills

Skills are workflow orchestrators defined in `.claude/skills/{name}/SKILL.md`. Each skill is a YAML frontmatter block followed by step-by-step Markdown instructions that Claude Code executes.

---

## Skill Frontmatter Schema

```yaml
---
name: {skill-name}
description: {natural language description — used for skill routing}
disable-model-invocation: true   # prevents the skill file itself from being "chatted with"
argument-hint: "[idea-id]"       # shown in autocomplete
allowed-tools: Read Write Agent Bash Skill
version: {MAJOR.MINOR.PATCH}
author: Aryan Curiel
---
```

---

## Skills by Category

### Idea Management

| Skill | Version | Trigger | What it does |
|---|---|---|---|
| `agora-add-idea` | 1.1.0 | "Add an idea: [description]" | Asks 9 targeted questions (one per readiness dimension), writes `ideas/{slug}/README.md` with real initial scores, updates `ideas_index.md` |
| `agora-list-ideas` | 1.0.0 | "Show me my ideas" | Reads `ideas_index.md`, displays all ideas in a table with score, progress bar, session count |
| `agora-show-idea` | 1.1.0 | "Show me the [name] idea" | Full idea details: readiness breakdown, constraints, notes, proposals, session history |
| `agora-add-note` | 1.0.0 | "Add a note to my [name] idea" | Lightweight note (feature/consideration/proposal/observation/risk) appended to idea's `## Notes` table without triggering a session |
| `agora-add-constraint` | 1.0.0 | "Add a constraint to my [name] idea" | Adds a hard requirement row to the `## Constraints` table in the idea README |

### Session Workflows

| Skill | Version | Trigger | What it does |
|---|---|---|---|
| `agora-run-debate` | 1.3.1 | "Run a debate on my [name] idea" | Full debate session: lead specialist selects roster, runs 2–3 rounds sequentially, scores after each round, writes report, appends analytics |
| `agora-brainstorm` | 1.1.1 | "Brainstorm on my [name] idea" | Full brainstorm: 5 dreamers run in parallel for 3 rounds, Skeptic grounds after rounds 2–3, writes report, appends analytics |

### Internal Sub-Skills (not user-invocable)

| Skill | Version | Called by | What it does |
|---|---|---|---|
| `agora-lead-specialist` | — | `agora-run-debate` | Reads the idea, selects best 3–4 specialist roster for current readiness gaps |
| `agora-score-round` | 1.1.0 | `agora-run-debate` | Meta-specialist: scores all 10 dimensions 0–10 after each round, returns JSON with new scores + synthesis paragraph |
| `agora-write-report` | 1.1.0 | `agora-run-debate` | Writes the full session Markdown report to `ideas/{slug}/sessions/` |
| `agora-write-brainstorm-report` | 1.0.0 | `agora-brainstorm` | Writes the brainstorm session Markdown report organized by horizon |

### Continuous Improvement

| Skill | Version | Trigger | What it does |
|---|---|---|---|
| `agora-review-specialists` | 1.3.0 | "Review specialists from the [slug] session" | Reads session transcript, evaluates each specialist on 5 criteria, writes versioned `PROPOSAL-v*.md` files, appends `specialists.jsonl` |
| `agora-list-proposals` | 1.0.0 | "Show me pending proposals" | Scans all `PROPOSAL-v*.md` files, scores by impact, tiers as Highly Recommended / Recommended / Optional |
| `agora-apply-specialist-update` | 1.1.0 | "Apply the [specialist-name] update" | Reads pending proposal, applies changes to agent definition, bumps version, cascades breaking changes, updates `CHANGELOG.md`, marks proposal applied |
| `agora-hire-specialists` | 1.0.0 | "Check if we need new specialists" | Reviews session coverage gaps, writes job-post Markdown files to `job-posts/` |
| `agora-build-specialist` | 1.0.0 | "Build the [slug] specialist" | Reads job-post, researches role, writes new agent definition in `.claude/agents/` |

### Analysis

| Skill | Version | Trigger | What it does |
|---|---|---|---|
| `agora-analyze` | 1.0.0 | "Analyze my sessions" | Reads `analytics/sessions.jsonl` and `analytics/specialists.jsonl`, generates trend report, KPI metrics, go/no-go validation |

### Design Guidance

| Skill | Version | Trigger | What it does |
|---|---|---|---|
| `knowledge-architect` | — | "What architecture should I use for [project/change]?" | Anthropic architecture guidance: Skills vs. Agents vs. Prompts vs. SDK primitives with decision rubrics |

---

## agora-run-debate — Detailed Step Sequence

This is the core workflow. Steps reference the actual SKILL.md logic.

### Phase 1: Setup (Steps 1–5)

1. Resolve idea slug from arguments or prompt user to pick from `ideas_index.md`
2. Read `ideas/{slug}/README.md` — extract current readiness scores and `## Constraints` section
3. Determine session number (count existing session rows + 1)
4. Read `agora-lead-specialist` skill
5. **Establish session KPIs** — select 3 lowest-scoring dimensions (target = min(score+2, 10)), select 2 most critical open questions. Print KPI block before Round 1.

### Phase 2: Roster Selection (Step 6)

6. Invoke `agora-lead-specialist` with idea slug + constraints. Returns JSON array of specialist names. Skeptic is always included.

### Phase 3: Debate Rounds (Steps 7–12)

For each round:

7. Print round header
8. For each specialist in roster — **invoke sequentially, one at a time** (each sees prior responses from this round)
   - Round 1 prompt: `[CONSTRAINTS]` + full idea description + readiness breakdown
   - Round 2+ prompt: `[CONSTRAINTS]` + idea name + `[ROUND_SYNTHESIS]` from previous round's score
   - All rounds also receive: `[PRIOR ROUND MESSAGES]` (last 10) + `[THIS ROUND SO FAR]`
9. Invoke `agora-score-round` with all round messages + current scores → returns JSON with new scores + synthesis
10. Extract `synthesis` → save as `[ROUND_SYNTHESIS]` for next round's specialist prompts. Print milestone update with score progress + dimension breakdown + open questions.
11. Update `ideas/{slug}/README.md` with new scores, open questions, best answers
12. Check termination: end if max rounds reached OR readiness ≥ 85%

### Phase 4: Finish (Steps 13–15)

13. Invoke `agora-write-report` with full session data + KPIs
14. Update Session History table in idea README
15. Update `ideas_index.md`

### Phase 5: KPI Evaluation & Analytics (Steps 16–17)

16. Evaluate KPIs:
    - Dimension target: Met (final ≥ target) / Partial (improved but below target) / Not met (no change)
    - Question: Yes (clear answer established) / Partial (progress made) / No (not addressed)
    - KPI score = (met×1.0 + partial×0.5) / total_kpis
17. Append one JSON record to `analytics/sessions.jsonl`

### Phase 6: Summary + Post-Session (Steps 18–19)

18. Print final summary with score delta, KPI results, weakest remaining dimensions
19. Print opt-in prompts for `agora-review-specialists` and `agora-hire-specialists` — **do not invoke automatically**

---

## agora-brainstorm — Detailed Step Sequence

### Phase 1: Setup (Steps 1–5)

1. Resolve idea slug
2. Read full idea context — name, description, open questions, existing proposals
3. Determine session number
4. Read `max_brainstorm_rounds` from `CLAUDE.md` (default: 3)
5. Print session header

### Phase 2: Rounds (Steps 6–9)

For each round (always run all rounds — no early exit):

6. Print round header with focus label (Round 1: free divergence, Round 2: cross-pollination, Round 3: sharpening)
7. Determine horizon assignments per dreamer for this round
8. **Invoke all 5 dreamers in parallel** (single message with 5 Agent calls)
   - Each receives: `[IDEA CONTEXT]` + `[BRAINSTORM HISTORY]` (all prior-round proposals) + `[HORIZON ASSIGNMENT]`
   - Round 2+: each must explicitly build on or fork at least one proposal from another dreamer
   - Print responses in canonical order: Futurist, Builder, User Advocate, Connector, Narrativist
9. After rounds 2 and 3 only: invoke `specialist-skeptic` in grounding mode (sequential, foreground)
   - Skeptic reviews all proposals so far, flags 2–3 structurally broken ones, asks 2 sharp questions

### Phase 3: Output (Steps 10–14)

10. Invoke `agora-write-brainstorm-report`
11. Update `ideas/{slug}/README.md` — merge proposals into `## Proposals` section organized by horizon (never delete existing proposals)
12. Update `ideas_index.md` — increment brainstorm count
13. Append to `analytics/brainstorms.jsonl` and `analytics/dreamers.jsonl` (one record per dreamer)
14. Print final summary: proposal counts by horizon, skeptic flags, strongest proposals per horizon

---

## agora-review-specialists — Detailed Step Sequence

1. Resolve session (slug + session number, or most recent)
2. Read full session report — extract specialists, transcripts, score changes
3. For each specialist: read agent definition, evaluate all contributions across all rounds on 5 criteria
4. Assign severity: none / minor / moderate / major
5. Determine version bump type: patch / minor / major
6. Check for major changes that need architecture review
7. Check for existing pending proposals — update rather than create new if one exists
8. Write `PROPOSAL-v{next-version}.md` for each specialist with severity ≥ minor
9. Append to `analytics/specialists.jsonl` (one record per specialist)
10. Print summary with proposals written, architectural flags, and apply commands

### Specialist Evaluation Criteria (Scored 1–5)

| Criterion | What it measures |
|---|---|
| `adherence` | Did they follow their stated role and output structure? |
| `specificity` | Did they name real technologies, numbers, companies — not vague generalities? |
| `novelty` | Did they introduce new information each round vs. repeating prior points? |
| `responsiveness` | Did they acknowledge and build on what other specialists said? |
| `impact` | Did their contributions measurably raise any readiness dimension score? |

---

## agora-apply-specialist-update — Detailed Step Sequence

1. Resolve specialist name and locate pending `PROPOSAL-v*.md`
2. Read full proposal — extract changes, change-type, breaking status, affected specialists
3. Validate: current agent version must match proposal's `current-version` (warn if stale)
4. For `major` changes: offer architecture review via `/knowledge-architect` before proceeding
5. Apply each proposed change to the agent definition (locate exact text block, replace)
6. Update `version` field in agent frontmatter to `proposed-version`
7. For breaking changes: identify affected specialists, offer cascade patch (auto-applies + bumps their PATCH version + updates their CHANGELOG)
8. Mark proposal `status: applied` + add `applied-date`
9. Update or create `CHANGELOG.md` for the target agent
10. Print summary

---

## Proposal Impact Scoring

Used by `agora-list-proposals` to rank pending proposals:

| Factor | Points |
|---|---|
| change-type: patch | +1 |
| change-type: minor | +2 |
| change-type: major | +4 |
| Breaking: yes | +2 |
| Each affected downstream specialist (max 3) | +1 each |
| Each `[major]` observed issue (max 2) | +1 each |
| Each `[moderate]` observed issue (max 1) | +0.5 |
| Proposal 14+ days old (stale) | +0.5 |

**Tiers:**
- **Highly Recommended** — impact ≥ 5, OR change-type is `major`, OR breaking is `yes`
- **Recommended** — impact ≥ 3
- **Optional** — everything else
