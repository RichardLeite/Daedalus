---
description: Review the current diff for correctness, security, and tests
agent: code-reviewer
subagent: true
---

Review the current change: $ARGUMENTS

Load the `code-review` skill.

Return findings ordered by severity, each with file and line, failure mode, and
the smallest fix. End with a verdict: approve, approve with comments, or request
changes.

Do not edit files.
