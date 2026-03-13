from datetime import date
from uuid import uuid4

from backend.app.models import DetectionMethod, Subscription, SubscriptionStatus
from backend.app.tasks.subscriptions import (
    enqueue_subscription_refreshes,
    process_subscription_refresh,
    recalculate_next_expected_charge,
)

from .conftest import FakeSession


def build_subscription(
    *,
    status=SubscriptionStatus.monitoring,
    last_charged_at=date(2026, 3, 1),
    recurrence_interval_days=30,
):
    return Subscription(
        id=uuid4(),
        user_id=uuid4(),
        retailer="sephora",
        product_name="Beauty Box",
        detection_method=DetectionMethod.order_pattern,
        status=status,
        last_charged_at=last_charged_at,
        recurrence_interval_days=recurrence_interval_days,
    )


def test_enqueue_subscription_refreshes_only_targets_refreshable_statuses():
    queued = []
    subscriptions = [
        build_subscription(status=SubscriptionStatus.monitoring),
        build_subscription(status=SubscriptionStatus.active),
        build_subscription(status=SubscriptionStatus.cancelled),
    ]

    queued_ids = enqueue_subscription_refreshes(subscriptions, delay_fn=queued.append)

    assert queued_ids == [str(subscriptions[0].id), str(subscriptions[1].id)]
    assert queued == queued_ids


def test_recalculate_next_expected_charge_returns_expected_date():
    subscription = build_subscription(last_charged_at=date(2026, 3, 1), recurrence_interval_days=15)

    assert recalculate_next_expected_charge(subscription) == date(2026, 3, 16)


def test_process_subscription_refresh_updates_next_expected_charge():
    subscription = build_subscription()
    session = FakeSession(subscription)

    result = process_subscription_refresh(session=session, subscription_id=str(subscription.id))

    assert result["status"] == "subscription_refreshed"
    assert subscription.next_expected_charge == date(2026, 3, 31)
    assert session.committed is True


def test_process_subscription_refresh_skips_when_schedule_data_is_missing():
    subscription = build_subscription(last_charged_at=None, recurrence_interval_days=None)
    session = FakeSession(subscription)

    result = process_subscription_refresh(session=session, subscription_id=str(subscription.id))

    assert result["status"] == "skipped_missing_schedule_data"
    assert session.committed is False
