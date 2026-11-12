---
name: End-to-End Testing
description: Design and run end-to-end tests for critical user flows with stable selectors and artifacts.
---

# End-to-end testing

Test the user-visible flow through the real stack.

## Procedure

1. List the critical user flows.
2. For each flow, write steps with observable outcomes.
3. Use stable selectors: role, label, test id. Avoid CSS chains.
4. Prepare isolated test data.
5. Run headless in CI and headed locally when debugging.
6. Capture screenshot, trace, and logs on failure.
7. Clean up data and sessions.

## Rules

- Do not depend on arbitrary sleeps; wait for a condition.
- Do not share state between tests.
- Do not use production data.
- Keep the suite small and high-value.
- Report flaky tests instead of retrying until green.

## Output

Flows covered, commands, artifacts, failures, and residual risk.
