---
name: Skill Creator
description: Create a concise, discoverable OpenCode skill with a clear description and procedure.
---

# Skill creator

Create a skill that the model can discover and apply.

## Procedure

1. Choose a unique lowercase kebab-case ID.
2. Write a one-sentence `description` that states when to use the skill.
3. Create `.opencode/skills/<id>/SKILL.md`.
4. Add:
   - goal
   - procedure
   - rules
   - output
5. Put long references in `references/` and scripts in `scripts/`.
6. Test by mentioning `@<id>` and checking that the instructions load.
7. Remove duplication with existing skills.

## Rules

- Keep the body short and actionable.
- Do not restate global instructions.
- Do not add a dependency for a small task.
- Make paths relative to the skill directory.
- Do not include secrets or machine-specific paths.

## Output

Skill ID, description, files, and a short verification note.
