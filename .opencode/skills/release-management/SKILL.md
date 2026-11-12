---
name: Release Management
description: Prepare a versioned release with changelog, tag, notes, and post-release verification.
---

# Release management

Ship a version with a clear record.

## Procedure

1. Confirm the release scope and version.
2. Update the changelog.
3. Run the full verification suite.
4. Tag the commit.
5. Create the GitHub release with `gh release create`.
6. Publish notes:
   - highlights
   - fixes
   - breaking changes
   - upgrade steps
7. Verify the published artifact.
8. Announce the release.

## Rules

- Follow semantic versioning.
- Do not release from a failing pipeline.
- Do not rewrite published tags.
- Include migration and rollback notes for breaking changes.
- Do not publish secrets or internal links.

## Output

Version, tag, release URL, checks, notes, and post-release verification.
