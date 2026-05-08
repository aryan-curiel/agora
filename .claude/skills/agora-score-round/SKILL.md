---
name: agora-score-round
description: Scores a completed debate round using the meta agent and updates the idea file. Invoked automatically by agora-run-debate. Not for direct user invocation.
user-invocable: false
version: 1.0.0
---

## Score a debate round

1. Receive: idea slug, list of round messages, current scores from caller context.
2. Invoke /agora-meta-specialist. Pass it:
   - The idea name and description (read from ideas/{slug}/README.md)
   - The previous scores
   - All messages from this round formatted as: "[Agent Name]\n{content}\n"
3. Parse the JSON response from agora-meta-specialist.
4. Calculate new readiness percentage: sum of all 10 scores / 10 * 10 = percentage.
5. Return to agora-run-debate: updated scores dict, new percentage, synthesis text, open questions list, best answers dict.
