from datetime import datetime, timezone
from uuid import uuid4

from backend.app.models import Order, OrderItem, OrderStatus, PriceSnapshot, SnapshotSource


def test_order_item_can_attach_to_order_and_snapshot():
    order = Order(
        id=uuid4(),
        user_id=uuid4(),
        retailer="nike",
        retailer_order_id="order-123",
        order_status=OrderStatus.pending,
        order_date=datetime.now(timezone.utc),
        subtotal=129.99,
    )
    order_item = OrderItem(
        id=uuid4(),
        order=order,
        user_id=order.user_id,
        product_name="Nike Shoes",
        product_url="https://example.com/nike-shoes",
        quantity=1,
        paid_price=129.99,
    )
    snapshot = PriceSnapshot(
        id=uuid4(),
        order_item=order_item,
        scraped_price=99.99,
        original_paid_price=129.99,
        snapshot_source=SnapshotSource.scheduled_job,
    )

    assert order_item.order is order
    assert snapshot.order_item is order_item
    assert snapshot.price_delta == 30.0
