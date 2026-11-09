"""Healthcheck and system status endpoint."""

from fastapi import APIRouter
from src.core.config import settings
from src.core.database import check_db_health

router = APIRouter()


@router.get("/health", tags=["System"])
async def get_health():
    """Verify backend health, database connectivity, and active autonomy mode."""
    db_ok = await check_db_health()
    return {
        "status": "online",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT.value,
        "autonomy_mode": settings.AUTONOMY_MODE.value,
        "database_connected": db_ok,
        "live_trading_enabled": False,  # Hard-coded safety indicator for Phase 1
    }
