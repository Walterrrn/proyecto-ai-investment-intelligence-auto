"""Risk engine status, limits, and position sizing calculation endpoints."""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Query
from src.core.config import settings
from src.services.risk_service import RiskService

router = APIRouter()


@router.get("/risk/limits", tags=["Risk Management"])
async def get_risk_limits() -> Dict[str, Any]:
    """Retrieve hard sovereign risk limits and safety parameters."""
    return {
        "max_risk_per_trade_pct": settings.RISK_MAX_PER_TRADE_PCT * 100,
        "max_aggregate_risk_pct": settings.RISK_MAX_AGGREGATE_PCT * 100,
        "max_daily_loss_pct": settings.RISK_MAX_DAILY_LOSS_PCT * 100,
        "max_weekly_loss_pct": settings.RISK_MAX_WEEKLY_LOSS_PCT * 100,
        "drawdown_review_pct": settings.RISK_DRAWDOWN_REVIEW_PCT * 100,
        "drawdown_halt_pct": settings.RISK_DRAWDOWN_HALT_PCT * 100,
        "leverage_allowed": settings.LEVERAGE_ALLOWED,
        "active_autonomy_mode": settings.AUTONOMY_MODE.value,
    }


@router.get("/risk/calculate-sizing", tags=["Risk Management"])
async def calculate_sizing(
    entry_price: float = Query(..., gt=0.0, description="Proposed entry price"),
    stop_loss_price: float = Query(..., gt=0.0, description="Proposed stop loss price"),
    risk_pct: Optional[float] = Query(None, description="Risk percentage (e.g. 0.0035 for 0.35%)")
) -> Dict[str, Any]:
    """
    Calculate mathematical position size using the risk formula:
    N = floor((Capital * Risk%) / (Entry - StopLoss))
    """
    service = RiskService()
    try:
        return service.calculate_position_sizing(entry_price, stop_loss_price, risk_pct)
    except ValueError as e:
        return {"error": str(e), "success": False}
