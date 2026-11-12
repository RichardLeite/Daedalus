---
description: Run the spec-to-review pipeline
agent: orchestrator
---

Run the Daedalus pipeline for: $ARGUMENTS

1. Refine the request with `business-analyst`.
2. Review the design with `architect` when the change is architectural.
3. Plan with `planner`.
4. Gate the plan with `tech-lead`.
5. Implement in TDD increments with `tdd-guide` and the right developer agent.
6. Review with `code-reviewer` and `security-reviewer`.
7. Verify tests and project checks.
8. Summarize evidence and remaining risk.

Stop and ask when a phase is ambiguous. Do not merge or push.
