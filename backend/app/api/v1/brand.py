"""Brand protection endpoints (stub)."""

from fastapi import APIRouter, Depends

from app.models.user import User
from app.services.auth import get_current_user

router = APIRouter()


@router.get("/status")
async def brand_status(current_user: User = Depends(get_current_user)):
    """Get brand protection status (stub)."""
    return {
        "status": "stub",
        "brands_monitored": 0,
        "alerts": [],
        "message": "Brand protection will be implemented in Phase 2",
    }


@router.post("/scan")
async def trigger_brand_scan(
    brand_name: str,
    current_user: User = Depends(get_current_user),
):
    """Trigger a brand protection scan (stub)."""
    return {
        "brand": brand_name,
        "status": "queued",
        "results": [],
        "message": "Full brand scan will be implemented in Phase 2",
    }
