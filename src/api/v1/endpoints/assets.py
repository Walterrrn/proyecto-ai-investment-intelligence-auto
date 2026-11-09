"""Asset catalogue endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from src.core.database import get_db
from src.models.asset import Asset, AssetClass, AllocationBucket

router = APIRouter()


class AssetRead(BaseModel):
    id: int
    symbol: str
    isin: Optional[str] = None
    name: str
    asset_class: str
    allocation_bucket: str
    currency: str
    exchange: str
    is_active: bool

    class Config:
        from_attributes = True


@router.get("/assets", response_model=List[AssetRead], tags=["Assets"])
async def list_assets(
    asset_class: Optional[str] = None,
    allocation_bucket: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List tracked assets, optionally filtered by class or allocation bucket."""
    stmt = select(Asset)
    if asset_class:
        stmt = stmt.where(Asset.asset_class == asset_class.upper())
    if allocation_bucket:
        stmt = stmt.where(Asset.allocation_bucket == allocation_bucket.upper())
    
    result = await db.execute(stmt)
    return list(result.scalars().all())
