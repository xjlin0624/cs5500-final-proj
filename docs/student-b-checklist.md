# Student B Checklist

## Week 1
- [x] Architecture documented in [architecture.md](/c:/Users/17645/OneDrive/文档/GitHub/cs5500-final-proj/docs/architecture.md)
- [x] Project management board assumptions documented in [project-management-board.md](/c:/Users/17645/OneDrive/文档/GitHub/cs5500-final-proj/docs/project-management-board.md)
- [x] Repo conventions, branching strategy, and PR/issue templates added
- [x] Docker Compose expanded for Postgres + Redis + API + worker + beat
- [x] GitHub Actions CI updated

## Week 2
- [x] Auto-deploy workflow scaffolding added
- [x] Backend and frontend Sentry initialization added
- [x] Render managed Postgres + Redis assumptions captured
- [x] Vercel deployment config added
- [x] `.env.example` expanded as the main env reference

## Week 3
- [x] Nike Playwright price scraper adapter added
- [x] Retry logic and rate limiting added for Nike and shared scraper path

## Week 4
- [x] Sephora Playwright price scraper adapter added
- [x] Celery Beat schedules cover price checks, subscription refresh, and delivery polling

## Week 5
- [x] Browser push registration API and frontend FCM plumbing added
- [x] High-priority alerts enqueue FCM push delivery

## Week 6
- [x] Nike and Sephora delivery polling adapters added
- [x] Retailer failures isolated with structured statuses and Redis-backed circuit state

## Week 7
- [x] Redis-backed LLM caching and throttling added
- [x] Cancellation guidance data store and read API added
- [x] Subscription refresh task hydrates guidance and schedule fields

## Week 8
- [x] Performance validation scripts added for price checks and dashboard load; fixture-backed price-check throughput and local preview dashboard load validated locally
- [x] Reliability notes documented in [scraper-reliability.md](/c:/Users/17645/OneDrive/文档/GitHub/cs5500-final-proj/docs/scraper-reliability.md)

## Week 9
- [x] Sentry triage flow documented in [operations.md](/c:/Users/17645/OneDrive/文档/GitHub/cs5500-final-proj/docs/operations.md)
- [x] Celery job performance improved with retailer-safe retries and no-op failure paths
- [x] Uptime monitoring guidance documented
- [x] Demo walkthrough added in [student-b-demo.md](/c:/Users/17645/OneDrive/文档/GitHub/cs5500-final-proj/docs/student-b-demo.md)
- [~] Amazon stretch implemented as a price adapter only; delivery polling remains out of scope for this repo state
