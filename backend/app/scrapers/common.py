import json
import re
from datetime import UTC, date, datetime
from typing import Any

from bs4 import BeautifulSoup

from ..models.enums import OrderStatus


_PRICE_RE = re.compile(r"(?<!\d)(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)")
_DATE_FORMATS = [
    "%B %d, %Y",
    "%b %d, %Y",
    "%B %d",
    "%b %d",
]


def make_soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def parse_price_text(value: str | None) -> float | None:
    if not value:
        return None
    match = _PRICE_RE.search(value.replace("$", "").strip())
    if not match:
        return None
    return float(match.group(1).replace(",", ""))


def extract_meta_price(soup: BeautifulSoup) -> float | None:
    selectors = [
        {"property": "product:price:amount"},
        {"name": "twitter:data1"},
        {"itemprop": "price"},
    ]
    for attrs in selectors:
        node = soup.find(attrs=attrs)
        if not node:
            continue
        price = parse_price_text(node.get("content") or node.get_text(" ", strip=True))
        if price is not None:
            return price
    return None


def _walk_json_ld(node: Any) -> float | None:
    if isinstance(node, dict):
        offers = node.get("offers")
        if isinstance(offers, dict):
            price = parse_price_text(str(offers.get("price") or offers.get("lowPrice") or ""))
            if price is not None:
                return price
        if node.get("@type") == "Product":
            price = parse_price_text(str(node.get("price") or ""))
            if price is not None:
                return price
        for value in node.values():
            price = _walk_json_ld(value)
            if price is not None:
                return price
    elif isinstance(node, list):
        for item in node:
            price = _walk_json_ld(item)
            if price is not None:
                return price
    return None


def extract_json_ld_price(soup: BeautifulSoup) -> float | None:
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = script.string or script.get_text(" ", strip=True)
        if not raw:
            continue
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            continue
        price = _walk_json_ld(parsed)
        if price is not None:
            return price
    return None


def extract_price_from_selectors(soup: BeautifulSoup, selectors: list[str]) -> float | None:
    for selector in selectors:
        node = soup.select_one(selector)
        if not node:
            continue
        price = parse_price_text(node.get_text(" ", strip=True))
        if price is not None:
            return price
    return None


def parse_date_from_text(value: str | None) -> date | None:
    if not value:
        return None
    cleaned = re.sub(r"\s+", " ", value.replace("Arrives by", "").replace("Estimated delivery", "")).strip(" :")
    today = datetime.now(UTC).date()
    for fmt in _DATE_FORMATS:
        try:
            parsed = datetime.strptime(cleaned, fmt).date()
        except ValueError:
            continue
        if "%Y" not in fmt:
            parsed = parsed.replace(year=today.year)
            if parsed < today:
                parsed = parsed.replace(year=today.year + 1)
        return parsed
    return None


def detect_order_status(text: str) -> OrderStatus | None:
    lowered = text.lower()
    if "delivered" in lowered:
        return OrderStatus.delivered
    if "cancelled" in lowered or "canceled" in lowered:
        return OrderStatus.cancelled
    if "returned" in lowered:
        return OrderStatus.returned
    if "in transit" in lowered or "on the way" in lowered:
        return OrderStatus.in_transit
    if "shipped" in lowered or "processing" in lowered:
        return OrderStatus.shipped
    if "ordered" in lowered or "pending" in lowered:
        return OrderStatus.pending
    return None


def page_requires_authentication(text: str) -> bool:
    lowered = text.lower()
    return "sign in" in lowered or "log in" in lowered or "sign into your account" in lowered
