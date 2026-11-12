---
description: Show the resolved Daedalus project context
agent: build
---

Run `daedalus context --json` from the project root.

Summarize:

1. Project name and root.
2. Profile and stack.
3. Initialization state.
4. Git branch and dirty state.
5. Global installation version.

Use the `--json` output as the source of truth. If the command is unavailable,
read `AGENTS.md` and `.opencode/project.json`.
