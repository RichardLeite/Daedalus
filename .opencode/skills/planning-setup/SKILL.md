---
name: Planning Setup
description: Establish project context, commands, conventions, and constraints before planning work.
---

# Planning setup

Load the right context before creating a plan.

## Procedure

1. Read the project `AGENTS.md`, `CONVENTIONS.md`, and `.opencode/project.json`.
2. Identify the stack and the package manager.
3. Find the commands for:
   - install
   - test
   - lint
   - type-check
   - build
   - run locally
4. Identify the relevant specs, ADRs, and entry points.
5. Note constraints: versions, environments, permissions, data.
6. Summarize the context in a short block.

## Rules

- Do not guess commands; read them from the repository.
- Do not load the whole codebase.
- Note missing tools as blockers.
- Keep the summary short enough to reuse.

## Output

Stack, commands, relevant files, constraints, and open questions.
