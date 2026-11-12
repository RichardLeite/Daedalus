---
description: Execute a modular spec with verification after each step
agent: orchestrator
---

Execute the spec at $ARGUMENTS

1. Read the spec and list its independent modules.
2. Order the modules by dependency.
3. Execute one module at a time.
4. After each module:
   - run its verification
   - report the result
   - stop on failure
5. Review the final diff.
6. Summarize completed modules, evidence, and gaps.

Do not parallelize modules that touch the same files.
