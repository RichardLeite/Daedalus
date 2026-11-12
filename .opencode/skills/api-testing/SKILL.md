---
name: API Testing
description: Test HTTP APIs for contract, auth, validation, errors, idempotency, and pagination.
---

# API testing

Verify the contract, not just the happy path.

## Procedure

1. Read the API spec or route definitions.
2. List endpoints and methods.
3. For each endpoint, test:
   - success response and schema
   - authentication and authorization
   - validation and malformed input
   - not found, conflict, and rate limit
   - idempotency where relevant
   - pagination and filtering
4. Use a local or test environment.
5. Capture request, response, and status code as evidence.
6. Report mismatches between spec and behavior.

## Rules

- Never use production credentials or data.
- Do not print tokens or personal data.
- Use parameterized requests.
- Keep tests independent.
- Clean up created resources.

## Output

Coverage, failures, evidence, and contract mismatches.
