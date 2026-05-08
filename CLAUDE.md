# Agora

Agora is a multi-agent debate system where AI specialists with different goals and expertise debate ideas to develop them from raw concepts into fully planned PoC/MVP specifications. Users add ideas, trigger debate sessions where specialist agents argue across multiple rounds, and receive structured planning outputs including a readiness score across 10 dimensions.

## How to work with ideas

Ideas live in `ideas/{slug}.md`. The index is `ideas_index.md`. Always keep the index in sync. When in doubt about an idea's current state, read its file first.

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
| Adding or creating an idea | `/add-idea` | "Add an idea: [describe it]" |
| Running, starting, or triggering a debate session | `/run-debate` | "Run a debate on my [name] idea" |
| Listing ideas or checking scores | `/list-ideas` | "Show me my ideas" |
| Viewing or showing a specific idea | `/show-idea` | "Show me the [name] idea" |
| Reviewing agent performance after a session | `/review-agents` | "Review agents from the [slug] session" |
| Applying an agent improvement proposal | `/apply-agent-update` | "Apply the [agent-name] update" |
| Designing or validating Anthropic architecture | `/anthropic-architect` | "What architecture should I use for [project/change]?" |

Scheduling is managed manually via the `ideas_index.md` schedule column.

## Session termination rules

A debate session ends when the first of these is hit:
- Max rounds reached (default: 4)
- Readiness score reaches target (default: 85%)
- Estimated token budget exceeded (default: 40,000 tokens)

## File naming conventions

- Ideas: `ideas/{slug}/README.md` where slug is lowercase-hyphenated name
- Sessions: `ideas/{slug}/sessions/{slug}-session-{n}-{YYYYMMDD}.md`
