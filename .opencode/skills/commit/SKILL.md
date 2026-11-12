---
name: Commit
description: Prepare a focused Conventional Commit without staging unrelated files.
---

# Commit

Create one coherent commit.

## Procedure

1. Inspect the working tree:
   - `git status --short`
   - `git diff`
   - `git diff --staged`
2. Identify one logical change.
3. Stage only the relevant files by path.
4. Write a Conventional Commit message:
   - `type(scope): imperative description`
   - Types: feat, fix, test, chore, docs, refactor, perf, build, ci.
5. Verify the staged diff.
6. Commit.

## Rules

- Never run `git add .` or `git add -A`.
- Never add co-authors unless asked.
- Do not commit secrets, generated files, or unrelated changes.
- Do not commit directly to `main` or `release`.
- Do not bypass hooks with `--no-verify`.

## Output

Commit hash, message, files, and any remaining unstaged changes.
