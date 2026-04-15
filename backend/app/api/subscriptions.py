from fastapi import APIRouter, HTTPException, status

from .deps import CurrentUser
from ..schemas.cancellation_guidance import CancellationGuidanceRead
from ..services.cancellation_guidance import get_cancellation_guidance


router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


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
