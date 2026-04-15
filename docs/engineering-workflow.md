# Engineering Workflow

## Branching
- Create feature branches from `main`.
- Use `feature/<area>-<summary>`, `fix/<area>-<summary>`, or `chore/<area>-<summary>`.
- Keep branches scoped to one logical unit of work when possible.

## Pull Requests
- Open a PR early when the shape is stable enough for review.
- Link the motivating issue or task in the PR description.
- Include local verification commands and screenshots for UI-affecting changes.
- Call out any required secrets, cloud resources, or migration steps.

## Review Expectations
- At least one teammate review before merging to `main`.
- Changes that touch schema, auth, deployment, or shared DTOs should include explicit reviewer notes about compatibility.
- Avoid force-pushing over teammate review context after review has started unless the branch is being rebased.

## Required Checks
- Backend lint
- Backend tests
- Scraper contract tests
- Frontend lint
- Frontend production build
- `docker compose config`

## Environment Variable Handling
- Never commit real secrets.
- Add every new variable to `.env.example`.
- Use graceful no-op behavior when optional integrations such as Sentry, Firebase, or deploy hooks are not configured.
- Use `VITE_` prefixes only for values that must be exposed to the frontend build.

## Merge and Deploy Rules
- `main` is the deploy branch.
- Pull requests validate CI only.
- Pushes to `main` may trigger Render and Vercel deployment hooks when those secrets are configured in GitHub Actions.
- Production config should be managed in Render/Vercel plus repository manifests, not in ad hoc local notes.
