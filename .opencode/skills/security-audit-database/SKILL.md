---
name: Database Security Audit
description: Audit database access, schema, queries, backups, and data protection controls.
---

# Database security audit

Protect the data at rest and in motion.

## Checklist

- Least-privilege database users.
- No shared admin credentials in application config.
- Parameterized queries everywhere.
- Encryption in transit and at rest.
- Backup access and restore testing.
- Personal and sensitive data classification.
- Retention and deletion behavior.
- Audit logging for privileged actions.
- Migration scripts that do not expose data.
- No credentials or connection strings in logs.

## Procedure

1. Map data stores, owners, and access paths.
2. Inspect schema, roles, and grants.
3. Inspect query construction in the application.
4. Verify backup and restore controls.
5. Classify findings.
6. Recommend the smallest remediation.

## Rules

- Do not edit production data.
- Do not print credentials or personal data.
- Do not run destructive queries.
- Report confirmed issues separately from hypotheses.

## Output

Findings with location, impact, severity, and remediation.
