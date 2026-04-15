from abc import ABC
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

from ..models.enums import OrderStatus


@dataclass(slots=True)
class PriceCheckResult:
    scraped_price: float
    currency: str = "USD"
    is_available: bool = True
    raw_payload: dict[str, Any] = field(default_factory=dict)
    source_url: str | None = None


@dataclass(slots=True)
class DeliveryCheckResult:
    order_status: OrderStatus | None = None
    estimated_delivery: date | None = None
    delivered_at: datetime | None = None
    tracking_number: str | None = None
    carrier: str | None = None
    carrier_status_raw: str | None = None
    raw_payload: dict[str, Any] = field(default_factory=dict)


class RetailerAdapter(ABC):
    retailer: str

    def fetch_current_price(self, order_item) -> PriceCheckResult:
        raise NotImplementedError

    def fetch_delivery_status(self, order) -> DeliveryCheckResult:
        raise NotImplementedError


class RetailerPriceAdapter(RetailerAdapter):
    pass
