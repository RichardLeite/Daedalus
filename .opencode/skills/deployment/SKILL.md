---
name: Deployment
description: Prepare, execute, verify, and roll back a deployment with explicit pre-flight checks.
---

# Deployment

Make the release boring and reversible.

## Procedure

1. Confirm the artifact and version.
2. Run pre-flight checks:
   - tests
   - migrations
   - configuration
   - secrets present but not printed
   - rollback artifact available
3. Deploy to the target environment.
4. Run smoke tests.
5. Watch errors, latency, and saturation.
6. Announce the result.
7. Roll back on a defined failure threshold.

## Rules

- Never deploy without a rollback path.
- Do not print secrets.
- Do not skip migrations or smoke tests.
- Do not deploy on a failing pipeline.
- Record the deployed commit and version.

## Output

Version, environment, checks, smoke result, monitoring window, and rollback.
