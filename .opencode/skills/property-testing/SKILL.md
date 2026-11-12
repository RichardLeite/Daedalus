---
name: Property-Based Testing
description: Discover invariants and test them with generated inputs and shrinking.
---

# Property-based testing

Test the rule, not a list of examples.

## Procedure

1. Identify invariants:
   - round-trip
   - idempotency
   - ordering
   - conservation
   - bounds
2. Choose a generator that produces realistic and edge-case inputs.
3. Write the property.
4. Run enough cases to be meaningful.
5. When it fails, use shrinking to find the minimal input.
6. Fix the code or the property, not the assertion.
7. Keep a regression example for the failing case.

## Rules

- Do not weaken the property to make it pass.
- Keep generators deterministic when a seed is needed.
- Separate generated data from production data.
- Report the seed and the minimal failing case.

## Output

Properties, generators, cases run, failures, shrinking results, and fix.
