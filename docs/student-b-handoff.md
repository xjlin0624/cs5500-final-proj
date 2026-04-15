# Student B Handoff

## Implemented
- Local/dev platform:
  - Postgres + Redis + API + worker + beat Compose stack
  - Playwright-capable backend image
  - expanded environment reference
- DevOps and automation:
  - PR/issue templates
  - CI workflow for backend/frontend/compose
  - deploy-hook workflow for `main`
  - Render and Vercel repo manifests
- Backend platform:
  - Sentry bootstrap for API and Celery
  - health and readiness endpoints
  - push token persistence and API
  - cancellation guidance datastore and API
  - subscription and push-token migrations
- Scrapers and jobs:
  - Nike and Sephora price adapters
  - Nike and Sephora delivery adapters
  - Amazon price adapter
  - Redis-backed rate limiting, retries, and circuit isolation
  - high-priority alert push dispatch task
  - Redis-backed Gemini caching and throttling
- Frontend:
  - Sentry initialization
  - browser push/Firebase service
  - settings integration for notification preferences

## Secrets / Cloud Setup Still Required
- `SENTRY_DSN` and `VITE_SENTRY_DSN`
- Firebase service account plus web Firebase config and VAPID key
- Render database/redis resources and deploy hook secret
- Vercel project + deploy hook secret if hook-based deploys are preferred
- Authenticated Playwright storage-state files for Nike/Sephora delivery pages

## Verification
- Backend tests:
  - `.\.venv313\Scripts\python -m pytest backend/tests`
- Backend lint:
  - `.\.venv313\Scripts\python -m ruff check backend`
- Local Playwright browser install:
  - `.\.venv313\Scripts\python -m playwright install chromium`
- Focused post-cleanup regression checks:
  - `.\.venv313\Scripts\python -m pytest backend/tests/test_imports.py backend/tests/test_celery_config.py backend/tests/test_scrapers.py backend/tests/test_health_push_and_guidance.py backend/tests/test_subscription_refresh.py -q`
- Frontend:
  - `cd frontend`
  - `npm run lint`
  - `npm run build`
- Compose:
  - `docker compose config`
- Price-check throughput:
  - `.\.venv313\Scripts\python backend/scripts/validate_price_check_performance.py --items 100 --target-seconds 300`
- Dashboard load:
  - `.\.venv313\Scripts\python backend/scripts/measure_dashboard_load.py --url http://127.0.0.1:4173/dashboard --target-ms 2000 --headless`

## Operational Notes
- Browser push is safe to enable only after Firebase secrets are present.
- Delivery polling degrades gracefully when retailer login state is missing.
- Amazon support is intentionally price-only in this implementation.
- The dashboard load measurement was exercised against a local `vite preview` instance; re-run it against a deployed environment before using it as a release gate.
