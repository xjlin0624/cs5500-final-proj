import logging
from typing import Any
from uuid import UUID

from celery import shared_task
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..core import get_settings
from ..db import session_scope
from ..models import OrderItem, PriceSnapshot, SnapshotSource
from ..scrapers import PriceCheckResult, get_price_adapter


logger = logging.getLogger(__name__)


def enqueue_candidate_price_checks(
    order_items: list[OrderItem],
    batch_size: int,
    delay_fn,
) -> list[str]:
    selected_ids: list[str] = []
    for order_item in order_items:
        if not order_item.is_monitoring_active or not order_item.product_url:
            continue
        selected_id = str(order_item.id)
        selected_ids.append(selected_id)
        delay_fn(selected_id)
        if len(selected_ids) >= batch_size:
            break
    return selected_ids


def process_order_item_price_check(
    session: Session,
    order_item_id: str | UUID,
    adapter_lookup=get_price_adapter,
) -> dict[str, Any]:
    stmt = (
        select(OrderItem)
        .options(selectinload(OrderItem.order))
        .where(OrderItem.id == UUID(str(order_item_id)))
    )
    order_item = session.execute(stmt).scalar_one_or_none()
    if order_item is None:
        return {"status": "skipped_missing_order_item", "order_item_id": str(order_item_id)}

    retailer = order_item.order.retailer if order_item.order else None
    adapter = adapter_lookup(retailer)
    if adapter is None:
        return {
            "status": "skipped_unsupported_retailer",
            "order_item_id": str(order_item.id),
            "retailer": retailer,
        }

    try:
        result: PriceCheckResult = adapter.fetch_current_price(order_item)
    except NotImplementedError:
        return {
            "status": "skipped_unsupported_retailer",
            "order_item_id": str(order_item.id),
            "retailer": retailer,
        }

    snapshot = PriceSnapshot(
        order_item_id=order_item.id,
        scraped_price=result.scraped_price,
        original_paid_price=order_item.paid_price,
        currency=result.currency,
        is_available=result.is_available,
        snapshot_source=SnapshotSource.scheduled_job,
    )
    session.add(snapshot)
    order_item.current_price = result.scraped_price
    session.commit()
    return {
        "status": "snapshot_created",
        "order_item_id": str(order_item.id),
        "retailer": retailer,
        "scraped_price": result.scraped_price,
    }


@shared_task(name="price_check_cycle")
def price_check_cycle() -> dict[str, Any]:
    settings = get_settings()
    with session_scope() as session:
        stmt = select(OrderItem).options(selectinload(OrderItem.order)).order_by(OrderItem.created_at.asc())
        order_items = list(session.execute(stmt).scalars().all())
        selected_ids = enqueue_candidate_price_checks(
            order_items=order_items,
            batch_size=settings.price_check_batch_size,
            delay_fn=check_order_item_price.delay,
        )
    logger.info("Enqueued %s price check tasks.", len(selected_ids))
    return {"status": "enqueued", "count": len(selected_ids), "order_item_ids": selected_ids}


@shared_task(name="check_order_item_price")
def check_order_item_price(order_item_id: str) -> dict[str, Any]:
    with session_scope() as session:
        result = process_order_item_price_check(session=session, order_item_id=order_item_id)
    logger.info("Processed price check for order item %s with status=%s.", order_item_id, result["status"])
    return result
