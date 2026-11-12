# Token policy

Keep context useful and small.

## Rules

- Load only the files needed for the current step.
- Prefer targeted searches over reading directories.
- Do not repeat a skill's instructions after loading it.
- Do not paste large logs; extract the failing lines.
- Summarize long outputs; keep the raw command available for reproduction.
- Use the cheapest agent that can do the task correctly.
- Keep `AGENTS.md` short; move details to rules or skills.
- Remove stale plans and duplicated context.
- Never compress security warnings, irreversible actions, or ambiguous
  multi-step instructions.

## Budget checks

- Is this context relevant to the current step?
- Is there a smaller file that answers the question?
- Can a subagent read it and return only the result?
- Is the model tier proportional to the task?
- Is the same information already in the conversation?
