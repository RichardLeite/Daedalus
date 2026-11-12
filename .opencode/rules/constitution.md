# Constitution

Non-negotiable engineering rules for Daedalus and for projects that use it.

## Rules

1. Never commit directly to `main` or `release`.
2. Never approve or merge a pull request on the user's behalf.
3. Every change must be reproducible, testable, and reversible.
4. Every behavior change needs a verification step.
5. Every durable decision needs a rationale; write an ADR when it is
   architectural.
6. No destructive migration without a rollback or forward-fix plan.
7. Do not expose secrets, credentials, tokens, or `.env` contents.
8. Do not resolve conflicts silently; report them.
9. Prefer small, focused changes over broad refactors.
10. Follow the project's conventions before personal preferences.

## Git

- Branch from the default branch.
- Use Conventional Commits.
- Do not force-push shared branches.
- Do not bypass hooks.
- Do not add co-authors unless asked.

## Review

- Review the diff, not the author.
- Block on correctness, security, and missing tests.
- Separate blocking findings from suggestions.
- State residual risk when approving.
