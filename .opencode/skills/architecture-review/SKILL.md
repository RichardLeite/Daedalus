---
name: Architecture Review
description: Review a design, ADR, or change for boundaries, coupling, failure modes, and operability.
---

# Architecture review

Evaluate the shape of the system before or after a change.

## Procedure

1. Read the goal, constraints, and the proposed design.
2. Map:
   - Modules and boundaries.
   - Data flow and ownership.
   - Synchronous and asynchronous paths.
   - External dependencies.
3. Check:
   - Coupling and cohesion.
   - Failure modes and recovery.
   - Scalability limits.
   - Security boundaries.
   - Operability: logs, metrics, deploy, rollback.
   - Reversibility of the decision.
4. Compare realistic alternatives.
5. Recommend one option and record the trade-offs.

## Rules

- Do not implement.
- Prefer the simplest design that meets the requirement.
- Name the failure modes.
- Distinguish reversible from irreversible decisions.
- Write an ADR for durable decisions.

## Output

Context, findings, alternatives, recommendation, consequences, and follow-ups.
