---
description: Run a layered review of the current change
agent: orchestrator
---

Run a four-layer review of: $ARGUMENTS

1. Static checks: project lint and type-check.
2. Tests: unit and affected integration tests.
3. Security: delegate to `security-reviewer`.
4. Code review: delegate to `code-reviewer`.

Report each layer, the evidence, and a final verdict. Do not edit production
code during the review.
