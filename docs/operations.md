# Operations

## Health Endpoints
- `GET /api/health`
  - Liveness probe for process-level uptime.
- `GET /api/health/ready`
  - Readiness probe for API + Postgres + Redis.
  - Returns `503` when database or Redis is unavailable.

## Uptime Monitoring
- Configure Render health checks against `/api/health/ready`.
- Add an external synthetic monitor if desired for the public frontend and API base URL.
- Keep frontend monitoring focused on Vercel deployment health and dashboard route availability.

## Sentry Triage Flow
1. Confirm environment and release tags on the event.
2. Check whether the failure came from `api`, `celery`, or `frontend`.
3. Group by retailer when scraper-related.
4. Determine whether the issue is:
   - secret/config missing
   - transient retailer/layout drift
   - code regression
5. If scraper drift is retailer-specific, verify whether the circuit is open and inspect recent task logs.

## Common Failure Modes
- Missing Firebase credentials: push task reports `disabled` and does not mark `alerts.push_sent_at`.
- Missing retailer session state: delivery scraper returns `scraper_not_ready`.
- Redis unavailable: readiness fails and cache/rate-limit features degrade.
- Retailer markup drift: scraper retries, then circuit-breaks after the configured threshold.

## Redis Coordination Keys
- Scraper rate limit: `ratelimit:scraper:<retailer>`
- Scraper circuit open flag: `circuit:scraper:<retailer>`
- Scraper failure counter: `circuit:failures:scraper:<retailer>`
- LLM cache: `llm:cache:<sha256>`
- LLM dedupe lock: `llm:dedupe:<sha256>`
- LLM rate limit: `llm:rate:global`

## Verification Commands
```powershell
docker compose up --build postgres redis api worker beat
.\.venv313\Scripts\python -m pytest backend/tests
cd frontend; npm run lint; npm run build
```
