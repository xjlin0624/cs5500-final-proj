# Student B Execution Plan

## Audit Summary
- Backend: `FastAPI`, `SQLAlchemy`, `Alembic`, `Celery`, Redis-backed worker scheduling.
- Frontend: `React` + `Vite`.
- Browser surface: Chrome extension with Amazon extraction and stubbed Target extraction.
- Existing B-adjacent code: Celery task scaffolding for price, delivery, and subscription refresh; Redis-aware settings; Docker Compose for API/worker/beat/redis; backend unit tests.
- Missing or incomplete: Postgres in Compose, Playwright scraper runtime, production deployment manifests, Sentry, browser push plumbing, Redis-backed LLM protections, cancellation guidance store, health endpoints, frontend CI/lint/build, and real Nike/Sephora/Amazon backend adapters.

## Execution Order
1. Add shared architecture and engineering workflow docs.
2. Normalize local and deployment configuration:
   - Docker Compose with Postgres + Redis + API + worker + beat
   - backend image updates for Playwright
   - `.env.example`, Render, Vercel, and GitHub workflow configuration
3. Add backend platform features:
   - settings expansion
   - health endpoints
   - backend/frontend Sentry hooks
   - subscription and push-token migrations
   - cancellation guidance datastore and API
4. Add Redis-backed coordination primitives:
   - scraper rate limiting and failure isolation
   - Gemini request caching and throttling
5. Implement scraper platform and adapters:
   - shared Playwright browser/session helpers
   - Nike and Sephora price + delivery adapters
   - Amazon price adapter as stretch
6. Wire Celery tasks to the new adapter platform and high-priority push delivery.
7. Add frontend FCM plumbing, settings integration, and Sentry bootstrap.
8. Add tests, performance validation utilities, and Student B handoff docs.

## Constraints
- Preserve existing APIs unless an additive change is required.
- Keep third-party integrations safe when credentials are absent.
- Avoid reverting unrelated user changes in the current dirty worktree.
- Prefer fixture-driven tests over live retailer/network dependence in CI.
