# Agora

Agora is a multi-agent debate system where AI specialists with different goals and expertise debate ideas to develop them from raw concepts into fully planned PoC/MVP specifications. Users add ideas, trigger debate sessions where specialist agents argue across multiple rounds, and receive structured planning outputs including a readiness score across 10 dimensions.

## How to work with ideas

Ideas live in `ideas/{slug}/README.md`. The index is `ideas_index.md`. Always keep the index in sync. When in doubt about an idea's current state, read its file first.

Constraints are hard requirements specialists must respect during all debate sessions (e.g. required tech stack, budget ceiling, product limitations). Add them with `/agora-add-constraint`. Specialists may only propose overriding a constraint using the explicit `⚠ CONSTRAINT OVERRIDE:` marker with a strong one-sentence justification.

## Readiness dimensions

| # | Dimension | What it measures |
|---|---|---|
| 1 | problem_statement | Is the problem clearly defined? |
| 2 | target_user | Is the target persona specific? |
| 3 | core_features | Is the MVP feature set scoped? |
| 4 | tech_stack | Has the technology approach been decided? |
| 5 | go_to_market | Is there a concrete first distribution plan? |
| 6 | key_risks | Have main risks been identified and addressed? |
| 7 | poc_scope | Is the minimum provable concept defined? |
| 8 | success_metrics | Are measurable success criteria defined? |
| 9 | monetization | Is there a revenue model? (mark N/A for personal/OSS) |
| 10 | budget_estimates | Are rough cost/effort estimates available per phase? |

## Available skills

| Trigger | Skill | Natural language |
|---|---|---|
| Adding or creating an idea | `/agora-add-idea` | "Add an idea: [describe it]" |
| Adding a note to an idea | `/agora-add-note` | "Add a note to my [name] idea" |
| Adding or updating a constraint on an idea | `/agora-add-constraint` | "Add a constraint to my [name] idea" |
| Running, starting, or triggering a debate session | `/agora-run-debate` | "Run a debate on my [name] idea" |
| Running or starting a brainstorm session on an idea | `/agora-brainstorm` | "Brainstorm on my [name] idea" |
| Listing ideas or checking scores | `/agora-list-ideas` | "Show me my ideas" |
| Viewing or showing a specific idea | `/agora-show-idea` | "Show me the [name] idea" |
| Reviewing specialist performance after a session | `/agora-review-specialists` | "Review specialists from the [slug] session" |
| Listing pending improvement proposals by impact | `/agora-list-proposals` | "Show me pending proposals" or "What should I apply next?" |
| Applying a specialist improvement proposal | `/agora-apply-specialist-update` | "Apply the [specialist-name] update" |
| Analyzing session and specialist performance trends | `/agora-analyze` | "Analyze my sessions" or "Show me performance trends" |
| Reviewing what new specialists to hire after a session | `/agora-hire-specialists` | "Check if we need new specialists" or "Run hiring review for [slug]" |
| Building a new specialist from a job-post | `/agora-build-specialist` | "Build the [slug] specialist" or "Hire the [slug] specialist" |
| Designing or validating Anthropic architecture | `/knowledge-architect` | "What architecture should I use for [project/change]?" |

Scheduling is managed manually via the `ideas_index.md` schedule column.

## Session defaults

| Setting | Default | Description |
|---|---|---|
| max_roster_size | 4 | Max specialists per session (including skeptic). |
| max_rounds | 3 | Max rounds when readiness < 30% (new idea). |
| max_rounds_partial | 2 | Max rounds when readiness ≥ 30% (partially developed). |
| max_brainstorm_rounds | 3 | Max rounds per brainstorm session. All rounds always run (no early exit). |
| readiness_target | 85% | Score at which a session ends early. |
| token_budget | 40,000 | Estimated token limit per session. |

To override any default, add a `## Session overrides` section below with `key: value` lines.

## Session termination rules

A debate session ends when the first of these is hit:
- Max rounds reached (see session defaults above)
- Readiness score reaches target (default: 85%)
- Estimated token budget exceeded (default: 40,000 tokens)

## File naming conventions

- Ideas: `ideas/{slug}/README.md` where slug is lowercase-hyphenated name
- Sessions: `ideas/{slug}/sessions/{slug}-session-{n}-{YYYYMMDD}.md`
- Brainstorm sessions: `ideas/{slug}/sessions/{slug}-brainstorm-{n}-{YYYYMMDD}.md`
