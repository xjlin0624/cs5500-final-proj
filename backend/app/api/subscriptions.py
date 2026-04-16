from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from .deps import CurrentUser
from .deps import DB
from ..models.subscription import Subscription
from ..schemas.cancellation_guidance import CancellationGuidanceRead
from ..schemas.subscription import SubscriptionRead
from ..services.cancellation_guidance import get_cancellation_guidance


router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("", response_model=list[SubscriptionRead])
def list_subscriptions(
    db: DB,
    current_user: CurrentUser,
) -> list[SubscriptionRead]:
    stmt = (
        select(Subscription)
        .where(Subscription.user_id == current_user.id)
        .order_by(Subscription.created_at.desc())
    )
    subscriptions = list(db.execute(stmt).scalars().all())

    results: list[SubscriptionRead] = []
    for subscription in subscriptions:
        guidance = get_cancellation_guidance(subscription.retailer)
        cancellation_url = subscription.cancellation_url or (
            guidance["cancellation_url"] if guidance else None
        )
        cancellation_steps = subscription.cancellation_steps or (
            "\n".join(guidance["steps"]) if guidance else None
        )
        cancellation_notes = guidance.get("notes") if guidance else None

        results.append(
            SubscriptionRead(
                id=subscription.id,
                user_id=subscription.user_id,
                retailer=subscription.retailer,
                product_name=subscription.product_name,
                product_url=subscription.product_url,
                detection_method=subscription.detection_method,
                recurrence_interval_days=subscription.recurrence_interval_days,
                estimated_monthly_cost=subscription.estimated_monthly_cost,
                last_charged_at=subscription.last_charged_at,
                next_expected_charge=subscription.next_expected_charge,
                status=subscription.status,
                cancellation_url=cancellation_url,
                cancellation_steps=cancellation_steps,
                cancellation_notes=cancellation_notes,
                source_order_ids=subscription.source_order_ids,
                created_at=subscription.created_at,
                updated_at=subscription.updated_at,
            )
        )

    return results


@router.get("/cancellation-guidance/{retailer}", response_model=CancellationGuidanceRead)
def get_retailer_cancellation_guidance(
    retailer: str,
    current_user: CurrentUser,
) -> CancellationGuidanceRead:
    del current_user
    guidance = get_cancellation_guidance(retailer)
    if guidance is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cancellation guidance not found",
        )
    return CancellationGuidanceRead(**guidance)
