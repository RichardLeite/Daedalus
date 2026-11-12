---
name: Observability
description: Add logs, metrics, traces, and alerts that make failures diagnosable without exposing sensitive data.
---

# Observability

Make the system explain its own failures.

## Procedure

1. Identify the critical paths and failure modes.
2. Add structured logs at boundaries:
   - input accepted or rejected
   - external call started and finished
   - state transition
   - error with context
3. Add metrics for rate, errors, and duration.
4. Add traces across service and database boundaries.
5. Add alerts only for actionable symptoms.
6. Verify that logs and traces do not contain secrets or personal data.

## Rules

- Use structured fields, not string concatenation.
- Include correlation or request IDs.
- Do not log full payloads by default.
- Do not create noisy alerts.
- Keep cardinality bounded.

## Output

Signals added, where they appear, how to query them, and privacy notes.
