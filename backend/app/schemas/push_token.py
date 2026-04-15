from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class PushTokenUpsert(BaseModel):
    token: str
    platform: str = "web"
    browser: str | None = None


class PushTokenRead(BaseModel):
    id: UUID
    user_id: UUID
    token: str
    platform: str
    browser: str | None
    is_active: bool
    last_seen_at: datetime

    model_config = {"from_attributes": True}
