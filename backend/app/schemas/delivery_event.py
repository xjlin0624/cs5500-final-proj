from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel, computed_field

from ..models.enums import DeliveryEventType

class DeliveryEventRead(BaseModel):
    id: UUID
    order_id: UUID
    event_type: DeliveryEventType
    previous_eta: date | None
    new_eta: date | None
    carrier_status_raw: str | None
    is_anomaly: bool
    scraped_at: datetime
    notes: str | None

    @computed_field
    @property
    def eta_slippage_days(self) -> int | None:
        if self.new_eta and self.previous_eta:
            return (self.new_eta - self.previous_eta).days
        return None

    model_config = {"from_attributes": True}
