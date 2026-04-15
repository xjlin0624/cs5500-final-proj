from contextlib import contextmanager
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

from ..core.settings import get_settings


def storage_state_path_for(retailer: str) -> Path:
    settings = get_settings()
    return Path(settings.playwright_storage_state_dir) / f"{retailer}.json"


@contextmanager
def browser_page(retailer: str, url: str) -> Page:
    settings = get_settings()
    storage_state_path = storage_state_path_for(retailer)

    with sync_playwright() as playwright:
        browser_launcher = getattr(playwright, settings.playwright_browser)
        browser = browser_launcher.launch(headless=settings.playwright_headless)
        context_kwargs = {"user_agent": settings.scraper_user_agent}
        if storage_state_path.exists():
            context_kwargs["storage_state"] = str(storage_state_path)
        context = browser.new_context(**context_kwargs)
        page = context.new_page()
        page.set_default_timeout(settings.playwright_timeout_ms)
        page.set_default_navigation_timeout(settings.playwright_navigation_timeout_ms)
        page.goto(url, wait_until="domcontentloaded")
        try:
            yield page
        finally:
            context.close()
            browser.close()
