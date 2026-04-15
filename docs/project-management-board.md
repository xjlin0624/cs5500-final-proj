# Project Management Board Assumptions

## Recommended Columns
- `Backlog`
- `Ready`
- `In Progress`
- `Review`
- `Blocked`
- `Done`

## Card Conventions
- One card per feature, infrastructure task, or bug.
- Prefix infra cards with `DevOps:` or `Scraper:` when the work spans multiple layers.
- Include the owner and target milestone/week in the card body.

## Definition of Ready
- Problem statement is clear.
- Acceptance criteria exist.
- Dependencies on schema, secrets, or deployment are called out.

## Definition of Done
- Code merged to `main`
- CI green
- Docs updated
- Required setup steps documented
- Demo impact noted when relevant
