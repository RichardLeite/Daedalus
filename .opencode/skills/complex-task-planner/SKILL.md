---
name: Complex Task Planner
description: Decompose a complex task into ordered, verifiable phases with dependencies and rollback.
---

# Complex task planner

Turn a large goal into a sequence of safe steps.

## Procedure

1. State the goal and definition of done.
2. Map the affected modules and boundaries.
3. Split into phases that can be verified independently.
4. For each phase, record:
   - goal
   - files or areas
   - change
   - verification
   - rollback
   - dependencies
5. Mark phases that can run in parallel.
6. Identify the riskiest phase and front-load a spike if needed.
7. Ask `tech-lead` to review medium and high risk plans.

## Rules

- Do not implement.
- Keep each phase small.
- Prefer reversible steps.
- Do not hide uncertainty.
- Do not plan work the code cannot support.

## Output

Goal, phases, dependency graph, verification, risks, and open questions.
