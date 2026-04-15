import random
import time
from collections.abc import Callable
from typing import TypeVar

from ..core.settings import get_settings
from ..services.redis_store import allow_rate_limit, is_circuit_open, record_circuit_failure, reset_circuit
from .exceptions import RetailerCircuitOpenError, RetailerNotReadyError, RetailerRateLimitedError, RetailerScrapeError, ScraperTransientError


T = TypeVar("T")


def run_scrape_with_guards(retailer: str, operation: str, scrape_fn: Callable[[], T]) -> T:
    settings = get_settings()
    scope = f"scraper:{retailer}"
    rate_key = f"ratelimit:{scope}"

    if is_circuit_open(scope):
        raise RetailerCircuitOpenError(f"{retailer} circuit is open; skipping {operation}.")
    if not allow_rate_limit(
        rate_key,
        limit=settings.scraper_rate_limit_per_minute,
        window_seconds=60,
    ):
        raise RetailerRateLimitedError(f"{retailer} scrape rate exceeded for {operation}.")

    last_error: Exception | None = None
    for attempt in range(1, settings.scraper_retry_attempts + 1):
        try:
            result = scrape_fn()
            reset_circuit(scope)
            return result
        except (RetailerCircuitOpenError, RetailerRateLimitedError, RetailerNotReadyError):
            raise
        except RetailerScrapeError as exc:
            last_error = exc
        except Exception as exc:  # pragma: no cover - defensive wrapper
            last_error = exc

        if attempt < settings.scraper_retry_attempts:
            base_delay = settings.scraper_backoff_base_seconds * (2 ** (attempt - 1))
            sleep_seconds = min(base_delay, settings.scraper_backoff_max_seconds) + random.uniform(0, 0.5)
            time.sleep(sleep_seconds)

    circuit_state = record_circuit_failure(
        scope,
        threshold=settings.scraper_circuit_failure_threshold,
        cooldown_seconds=settings.scraper_circuit_cooldown_seconds,
    )
    message = f"{retailer} {operation} failed after retries."
    if circuit_state.get("open"):
        message = f"{message} Circuit opened for cooldown."
    raise ScraperTransientError(f"{message} Last error: {last_error}")
