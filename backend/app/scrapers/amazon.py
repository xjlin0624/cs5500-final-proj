from .base import PriceCheckResult, RetailerPriceAdapter
from .common import extract_json_ld_price, extract_meta_price, extract_price_from_selectors, make_soup
from .exceptions import RetailerUnsupportedError, ScraperTransientError
from .playwright_client import browser_page
from .reliability import run_scrape_with_guards


_AMAZON_PRICE_SELECTORS = [
    "#priceblock_ourprice",
    "#priceblock_dealprice",
    ".a-price .a-offscreen",
]


def parse_amazon_price_html(html: str, *, source_url: str | None = None) -> PriceCheckResult:
    soup = make_soup(html)
    price = (
        extract_price_from_selectors(soup, _AMAZON_PRICE_SELECTORS)
        or extract_meta_price(soup)
        or extract_json_ld_price(soup)
    )
    if price is None:
        raise ScraperTransientError("Amazon price not found on page.")
    return PriceCheckResult(
        scraped_price=price,
        currency="USD",
        is_available=True,
        raw_payload={"retailer": "amazon"},
        source_url=source_url,
    )


class AmazonAdapter(RetailerPriceAdapter):
    retailer = "amazon"

    def fetch_current_price(self, order_item) -> PriceCheckResult:
        def scrape() -> PriceCheckResult:
            with browser_page(self.retailer, order_item.product_url) as page:
                return parse_amazon_price_html(page.content(), source_url=order_item.product_url)

        return run_scrape_with_guards(self.retailer, "price_check", scrape)

    def fetch_delivery_status(self, order):
        raise RetailerUnsupportedError("Amazon delivery polling is not implemented in this repository.")
