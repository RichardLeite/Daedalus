---
description: Switch the response style between Caveman levels
agent: orchestrator
---

Switch the response style to: $ARGUMENTS

Valid values:

- `lite` — remove filler only. Default.
- `full` — drop articles, fragments allowed.
- `ultra` — abbreviate prose, use arrows for causality.
- `off` — normal prose.

Apply the style to this session. Do not announce the mode. Preserve the user's
language and all technical terms, code, and error strings.

For a persistent change, tell the user to edit the Communication style section
in `AGENTS.md`.
