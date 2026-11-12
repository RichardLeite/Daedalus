---
name: Database Migrations
description: Plan and apply reversible database migrations with data safety and rollback.
---

# Database migrations

Change the schema without losing data.

## Procedure

1. Read the current schema and migration history.
2. State the target model and the migration path.
3. Prefer additive changes:
   - add nullable column
   - backfill
   - add constraint
   - remove old column in a later release
4. Write the migration and the rollback.
5. Test on a copy of realistic data.
6. Measure lock time and impact.
7. Apply in a controlled window if needed.

## Rules

- Never run destructive changes on production without approval.
- Always provide a rollback or a forward-fix plan.
- Do not mix schema and data changes without a reason.
- Add indexes only for a known query pattern.
- Do not log credentials or connection strings.

## Output

Migration, rollback, data steps, tests, lock impact, and risk.
