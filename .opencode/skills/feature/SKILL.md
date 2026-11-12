---
name: Feature
description: Implement a feature from an accepted spec, in small verified increments.
---

# Feature

Deliver the behavior described by the spec.

## Procedure

1. Read the spec, acceptance criteria, and project conventions.
2. Identify the smallest first increment.
3. Confirm the affected layers and dependencies.
4. Implement the increment.
5. Add or update tests for the acceptance criteria.
6. Run the project's test, lint, and type-check commands.
7. Update documentation when behavior changes.
8. Repeat until the spec is covered.

## Rules

- Do not add behavior outside the spec.
- Do not introduce a new pattern without approval.
- Keep changes reviewable.
- Handle loading, empty, error, and success states where relevant.
- Do not skip verification.

## Output

Acceptance criteria covered, changed files, tests, evidence, and gaps.
