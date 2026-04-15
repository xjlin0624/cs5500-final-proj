from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text

from .deps import DB
from ..services.redis_store import ping_redis


router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready")
def readiness_check(db: DB) -> dict[str, dict[str, bool] | str]:
    database_ok = True
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        database_ok = False

    redis_ok = ping_redis()
    ready = database_ok and redis_ok
    if not ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "degraded",
                "dependencies": {
                    "database": database_ok,
                    "redis": redis_ok,
                },
            },
        )

    return {
        "status": "ok",
        "dependencies": {
            "database": database_ok,
            "redis": redis_ok,
        },
    }
