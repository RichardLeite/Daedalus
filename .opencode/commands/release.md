---
description: Prepare a versioned release
agent: devops-engineer
---

Prepare a release for: $ARGUMENTS

Load the `release-management` and `deployment` skills.

1. Confirm the version and scope.
2. Update the changelog.
3. Run the full verification suite.
4. Create the tag and GitHub release with `gh`.
5. Provide rollback and upgrade notes.
6. Verify the published artifact.

Do not release from a failing pipeline.
