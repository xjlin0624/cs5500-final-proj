from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from ..models.order_item import OrderItem


@dataclass(slots=True)
class PriceCheckResult:
    scraped_price: float
    currency: str = "USD"
    is_available: bool = True
    raw_payload: dict[str, Any] = field(default_factory=dict)


class RetailerPriceAdapter(ABC):
    retailer: str

    @abstractmethod
    def fetch_current_price(self, order_item: OrderItem) -> PriceCheckResult:
        raise NotImplementedError
