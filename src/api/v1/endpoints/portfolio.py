"""Portfolio tracking and allocation simulation endpoints."""

from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.services.portfolio_service import PortfolioService

router = APIRouter()


@router.get("/portfolio/allocation", tags=["Portfolio"])
async def get_portfolio_allocation(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get consolidated portfolio allocation breakdown across the 4 asset buckets
    (Long Term 50%, Tactical 15%, Crypto 10%, Liquidity 25%) and deviation metrics.
    """
    service = PortfolioService(db)
    return await service.get_allocation_breakdown()
