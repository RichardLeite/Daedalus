---
name: Pull Request
description: Prepare and open a pull request with context, evidence, risk, and rollback.
---

# Pull request

Open a reviewable pull request.

## Procedure

1. Confirm the branch is not `main` or `release`.
2. Inspect the diff and the commits.
3. Run the project's tests and linters.
4. Write:
   - What changed.
   - Why.
   - Evidence.
   - Risks.
   - Rollback.
   - Linked issue or task.
5. Create the PR with `gh pr create`.
6. Report the URL and the checks.

## Rules

- Use `gh` for GitHub operations.
- Do not merge or approve on the user's behalf.
- Do not force-push.
- Do not include secrets or personal data.
- Keep the diff focused.
- Request review from the right owner when known.

## Output

PR URL, title, summary, checks, and follow-ups.
