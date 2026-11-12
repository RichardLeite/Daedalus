---
name: API Security Audit
description: Audit an HTTP API for authentication, authorization, injection, rate limits, and data exposure.
---

# API security audit

Look for exploitable behavior, not style.

## Checklist

- Authentication on every non-public endpoint.
- Authorization checked per object, not just per route.
- Input validation and output encoding.
- SQL, command, template, and header injection.
- SSRF and unsafe URL fetching.
- CORS policy.
- Rate limits and abuse controls.
- Error responses that leak stack traces or internals.
- Secrets in code, logs, and fixtures.
- Dependency and supply-chain changes.
- Personal data in logs and responses.

## Procedure

1. Map endpoints and trust boundaries.
2. Test the highest-risk paths.
3. Confirm the attack path before reporting.
4. Classify severity.
5. Recommend the smallest remediation.

## Rules

- Do not edit code.
- Do not test against production without approval.
- Do not include exploit payloads in public reports.
- Distinguish confirmed issues from hypotheses.

## Output

Findings with location, attack path, impact, severity, and remediation.
