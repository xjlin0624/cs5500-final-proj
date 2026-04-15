from __future__ import annotations

import argparse
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class _Result:
    def __init__(self, value):
        self.value = value

    def scalar_one_or_none(self):
        return self.value


class _Session:
    def __init__(self, order_item):
        self.order_item = order_item
        self.added = []

    def execute(self, _stmt):
        return _Result(self.order_item)

    def add(self, value):
        self.added.append(value)

    def commit(self):
        return None


@dataclass
class _Adapter:
    price: float

    def fetch_current_price(self, _order_item):
        from backend.app.scrapers import PriceCheckResult

        return PriceCheckResult(scraped_price=self.price, currency="USD", is_available=True)


def _build_item(index: int):
    from backend.app.models import Order, OrderItem, OrderStatus

    order = Order(
        id=uuid4(),
        user_id=uuid4(),
        retailer="nike",
        retailer_order_id=f"perf-{index}",
        order_status=OrderStatus.pending,
        order_date=datetime.now(timezone.utc),
        subtotal=100.0,
        order_url=f"https://example.com/order/{index}",
    )
    return OrderItem(
        id=uuid4(),
        order_id=order.id,
        order=order,
        user_id=order.user_id,
        product_name=f"Item {index}",
        product_url=f"https://example.com/item/{index}",
        quantity=1,
        paid_price=100.0,
        is_monitoring_active=True,
    )


def main() -> int:
    from backend.app.tasks.price_monitoring import process_order_item_price_check

    parser = argparse.ArgumentParser(description="Validate fixture-based price check throughput.")
    parser.add_argument("--items", type=int, default=100)
    parser.add_argument("--target-seconds", type=float, default=300.0)
    args = parser.parse_args()

    started = time.perf_counter()
    for index in range(args.items):
        order_item = _build_item(index)
        session = _Session(order_item)
        process_order_item_price_check(
            session=session,
            order_item_id=order_item.id,
            adapter_lookup=lambda _retailer: _Adapter(price=90.0),
            prefs_lookup=lambda _uid: None,
            existing_alert_lookup=lambda _session, _id: None,
        )
    elapsed = time.perf_counter() - started

    print(f"Processed {args.items} fixture-backed price checks in {elapsed:.2f}s.")
    if elapsed > args.target_seconds:
        print(f"FAILED: target was {args.target_seconds:.2f}s.")
        return 1

    print(f"PASSED: target was {args.target_seconds:.2f}s.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
