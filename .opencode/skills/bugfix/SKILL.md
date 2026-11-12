---
name: Bugfix
description: Reproduce, isolate, fix, and prove a bug fix with a regression test.
---

# Bugfix

Fix the cause, not the symptom.

## Procedure

1. Reproduce the failure with the smallest command or test.
2. Capture the error, environment, and recent changes.
3. Reduce the case until the cause is isolated.
4. State the root cause with evidence.
5. Write a regression test that fails for the expected reason.
6. Apply the smallest fix.
7. Run the regression test and the relevant suite.
8. Report the cause, fix, and evidence.

## Rules

- Do not broaden the scope.
- Do not weaken tests or catch errors broadly.
- Do not fix unrelated code in the same change.
- Add a regression test unless the user explicitly waives it.
- Report uncertainty instead of guessing.

## Output

Reproduction, root cause, fix, regression test, verification, and residual risk.
