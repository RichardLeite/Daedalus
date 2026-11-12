# Conventions

Generic engineering conventions for projects using Daedalus. Project-specific
conventions take precedence.

## Naming

- Files and directories: `kebab-case`.
- Python: `snake_case` for functions and variables, `PascalCase` for classes.
- TypeScript/JavaScript: `camelCase` for functions and variables, `PascalCase`
  for components and types.
- Environment variables: `UPPER_SNAKE_CASE`.
- Branches: `type/short-scope`, for example `feat/user-invite`.

## Commits

Use Conventional Commits:

```text
type(scope): description
```

Types: `feat`, `fix`, `test`, `chore`, `docs`, `refactor`, `perf`, `build`, `ci`.

- Imperative, lowercase description.
- One logical change per commit.
- No co-authors unless explicitly requested.
- Reference the issue or task when one exists.

## Branches

- Never commit directly to `main` or `release`.
- Branch from the default branch.
- Rebase only on your own unpublished branch.
- Do not rewrite shared history.

## Pull requests

- Explain what changed, why, evidence, risks, and rollback.
- Keep the diff focused.
- Include tests or a clear explanation of why they are not needed.
- Do not merge your own PR without review unless the project allows it.

## Code

- Follow the existing structure and style before introducing a new pattern.
- Prefer explicit names over abbreviations.
- Handle errors at boundaries; do not swallow them.
- Validate input at the edge.
- Keep functions small and cohesive.
- Avoid dead code and commented-out blocks.

## Tests

- Test behavior, not implementation details.
- Cover the happy path, boundaries, and expected failures.
- Keep tests deterministic and independent.
- A bug fix includes a regression test when practical.

## Security

- Never commit secrets, tokens, credentials, or `.env` files.
- Treat user input as untrusted.
- Use parameterized queries.
- Do not log personal or sensitive data.
- Report suspected vulnerabilities privately.

## Documentation

- Write public documentation in English.
- Keep examples runnable and cross-platform.
- Prefer short, task-oriented guides over long reference pages.
- Update documentation when behavior changes.

## Cross-platform

- Use `pathlib` instead of manual path separators in Python.
- Avoid shell-specific commands in reusable scripts.
- Use UTF-8 explicitly when reading or writing text.
- Test on Linux, macOS, and Windows when the project supports them.
