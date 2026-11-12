# Decision tree

Route work by risk and task type.

## Risk

- **Low**: read-only, typo, rename, formatting, isolated UI tweak. Single agent,
  no review gate.
- **Medium**: business rule, integration, non-destructive schema change, simple
  auth, test improvement. Plan, implement, review.
- **High**: financial logic, auth overhaul, personal data, production deploy,
  destructive migration, breaking API change. Plan, design review, security
  review, staged rollout.

## Route

| Task | Primary | Secondary |
|---|---|---|
| Discovery | `explorer` | `repo-scan` |
| Backend | `backend-dev` | `code-reviewer` |
| Frontend | `frontend-dev` | `ux-analyzer` |
| Database | `database-dev` | `security-reviewer` |
| Test-first | `tdd-guide` | `qa-engineer` |
| Small defined change | `implementer` | `code-reviewer` |
| Code review | `code-reviewer` | `security-reviewer` |
| Security | `security-reviewer` | `architect` |
| Architecture | `architect` | `tech-lead` |
| Plan review | `tech-lead` | `architect` |
| Debugging | `debugger` | `code-reviewer` |
| Pull request | `pr-reviewer` | `security-reviewer` |
| UX | `ux-analyzer` | `frontend-dev` |
| Images | `image-analyzer` | `frontend-dev` |
| CI/CD | `devops-engineer` | `security-reviewer` |
| QA | `qa-engineer` | `tdd-guide` |
| Requirements | `business-analyst` | `product-manager` |
| Product | `product-manager` | `business-analyst` |
| Sprint | `scrum-master` | `product-manager` |
| Planning | `planner` | `tech-lead` |
| Cost | `token-manager` | `planner` |

## Escalation

- Ambiguity: ask the user.
- Conflicting agent recommendations: `tech-lead`, then the user.
- Security disagreement: `security-reviewer` blocks until resolved.
- Architecture disagreement: `architect` records the ADR; `tech-lead` gates.
