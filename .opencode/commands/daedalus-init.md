---
description: Initialize or update the Daedalus project layer
agent: build
---

Run `daedalus init $ARGUMENTS` from the project root.

1. If `daedalus` is not on PATH, use `python -m daedalus init $ARGUMENTS`.
2. Show the plan with `--plan` first when the user did not ask for an immediate
   change.
3. Ask for the profile and integrations when they are not provided.
4. Apply with `--yes` only after the plan is clear.
5. Never overwrite user files.
6. Summarize every file created or changed.
7. Suggest the next command.
