---
description: Prepare a focused Conventional Commit
agent: orchestrator
---

Prepare a commit for: $ARGUMENTS

Load the `commit` skill.

1. Inspect the working tree and staged diff.
2. Identify one logical change.
3. Stage only the relevant files by path.
4. Write a Conventional Commit message.
5. Show the staged diff summary.
6. Commit only after confirmation when the user did not ask for an immediate
   commit.

Never run `git add .` or `git add -A`. Never bypass hooks.
