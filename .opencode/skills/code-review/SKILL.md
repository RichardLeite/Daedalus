---
name: Code Review
description: Structured code review of a diff, with severity classification and actionable findings.
---

# Code review

Review the change, not the whole repository.

## Procedure

1. Inspect the diff:
   - `git diff --stat`
   - `git diff`
2. Read the surrounding code for context.
3. Check:
   - Correctness against the stated behavior.
   - Edge cases, nulls, empty values, and error paths.
   - Security: input validation, auth, secrets, injection.
   - Performance: N+1 queries, unnecessary work, unbounded loops.
   - Tests: do they prove the behavior?
   - Maintainability: naming, duplication, dead code.
4. Classify each finding:
   - Critical: wrong behavior, data loss, security, broken build.
   - High: likely bug, missing validation, missing regression test.
   - Medium: maintainability or performance risk.
   - Low: style or clarity.
5. Report findings first, then a verdict.

## Rules

- Cite file and line.
- Explain the failure mode, not a preference.
- Do not edit files.
- Do not request unrelated changes unless they block correctness.
- If there are no findings, say so and name the residual risk.

## Output

Findings by severity, then: approve, approve with comments, or request changes.
