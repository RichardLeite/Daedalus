---
name: Repository Scan
description: Map a repository's structure, entry points, commands, and conventions without editing files.
---

# Repository scan

Build a fast, accurate map of a repository.

## Procedure

1. List the top-level structure.
2. Read the README, `AGENTS.md`, and package manifests.
3. Identify:
   - entry points
   - main modules
   - data layer
   - test layout
   - CI configuration
4. Find the build, test, lint, and run commands.
5. Note conventions and generated directories.
6. List the files most relevant to the current task.

## Rules

- Read-only.
- Do not dump large files.
- Prefer targeted searches.
- Mark generated or vendored code.
- Report uncertainty.

## Output

Structure, entry points, commands, conventions, relevant files, and risks.
