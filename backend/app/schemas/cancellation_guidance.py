from pydantic import BaseModel


class CancellationGuidanceRead(BaseModel):
    retailer: str
    cancellation_url: str
    steps: list[str]
    notes: str | None = None
