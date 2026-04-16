from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, computed_field

from ..models.enums import DetectionMethod, SubscriptionStatus


class SubscriptionRead(BaseModel):
    id: UUID
    user_id: UUID
    retailer: str
    product_name: str
    product_url: str | None
    detection_method: DetectionMethod
    recurrence_interval_days: int | None
    estimated_monthly_cost: float | None
    last_charged_at: date | None
    next_expected_charge: date | None
    status: SubscriptionStatus
    cancellation_url: str | None = None
    cancellation_steps: str | None = None
    cancellation_notes: str | None = None
    source_order_ids: list[UUID] | None = None
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def cancellation_steps_list(self) -> list[str]:
        if not self.cancellation_steps:
            return []
        return [
            step.strip()
            for step in self.cancellation_steps.splitlines()
            if step.strip()
        ]

