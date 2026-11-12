---
name: Mutation Testing
description: Run mutation testing, interpret survivors, and strengthen the test suite.
---

# Mutation testing

Measure whether the tests detect real defects.

## Procedure

1. Run the mutation tool on a focused module.
2. Record the mutation score.
3. Triage survivors:
   - equivalent mutant: no behavior change
   - missing test: real gap
   - weak assertion: test does not check the result
4. Add or strengthen the smallest test that kills the mutant.
5. Re-run and compare.
6. Keep the runtime practical.

## Rules

- Do not chase a score with meaningless assertions.
- Exclude generated code.
- Keep the scope focused.
- Report equivalent mutants instead of silencing them silently.
- Do not weaken production code to satisfy a mutant.

## Output

Scope, score, survivors, tests added, and new score.
