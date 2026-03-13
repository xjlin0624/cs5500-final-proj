from datetime import datetime, timezone
from uuid import uuid4

from backend.app.models import Order, OrderItem, OrderStatus, PriceSnapshot
from backend.app.scrapers import PriceCheckResult
from backend.app.tasks.price_monitoring import (
    enqueue_candidate_price_checks,
    process_order_item_price_check,
)

from .conftest import FakeSession


class FakeAdapter:
    def fetch_current_price(self, _order_item):
        return PriceCheckResult(
            scraped_price=79.99,
            currency="USD",
            is_available=True,
            raw_payload={"source": "fake"},
        )


def build_order_item(*, active=True, product_url="https://example.com/item", retailer="nike"):
    order = Order(
        id=uuid4(),
        user_id=uuid4(),
        retailer=retailer,
        retailer_order_id=f"order-{uuid4()}",
        order_status=OrderStatus.pending,
        order_date=datetime.now(timezone.utc),
        subtotal=120.0,
    )
    return OrderItem(
        id=uuid4(),
        order=order,
        user_id=order.user_id,
        product_name="Tracked Item",
        product_url=product_url,
        quantity=1,
        paid_price=120.0,
        is_monitoring_active=active,
    )


def test_enqueue_candidate_price_checks_only_picks_active_items_with_product_url():
    selected = []
    order_items = [
        build_order_item(active=True, product_url="https://example.com/1"),
        build_order_item(active=False, product_url="https://example.com/2"),
        build_order_item(active=True, product_url=""),
        build_order_item(active=True, product_url="https://example.com/3"),
    ]

    queued_ids = enqueue_candidate_price_checks(order_items, batch_size=2, delay_fn=selected.append)

    assert queued_ids == [str(order_items[0].id), str(order_items[3].id)]
    assert selected == queued_ids


def test_process_order_item_price_check_creates_snapshot_and_updates_current_price():
    order_item = build_order_item()
    session = FakeSession(order_item)

    result = process_order_item_price_check(
        session=session,
        order_item_id=str(order_item.id),
        adapter_lookup=lambda _retailer: FakeAdapter(),
    )

    assert result["status"] == "snapshot_created"
    assert order_item.current_price == 79.99
    assert session.committed is True
    assert len(session.added) == 1
    assert isinstance(session.added[0], PriceSnapshot)


def test_process_order_item_price_check_skips_unsupported_retailer():
    order_item = build_order_item(retailer="amazon")
    session = FakeSession(order_item)

    result = process_order_item_price_check(
        session=session,
        order_item_id=str(order_item.id),
        adapter_lookup=lambda _retailer: None,
    )

    assert result["status"] == "skipped_unsupported_retailer"
    assert session.committed is False
    assert session.added == []
