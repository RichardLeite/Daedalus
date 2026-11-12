---
name: QA Test Plan
description: Produce a test plan with cases, boundaries, regression scenarios, and execution evidence.
---

# QA test plan

Prove the behavior and expose the gaps.

## Procedure

1. Read the requirement, spec, and diff.
2. List behaviors to verify.
3. Cover:
   - happy path
   - boundaries
   - invalid input
   - permissions
   - failure and retry
   - regression of related behavior
4. Choose the cheapest reliable test level.
5. Define test data and environment.
6. Run the tests or document the exact commands.
7. Report coverage gaps.

## Rules

- Do not change production code.
- Do not weaken assertions.
- Keep tests deterministic.
- Report flaky tests instead of retrying until green.
- Prefer behavior over implementation.

## Output

Test plan, cases, commands, evidence, gaps, and residual risk.
