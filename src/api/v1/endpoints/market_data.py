"""Market data and intelligence REST endpoints."""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.models.asset import Asset
from src.models.market_data import MarketDataOHLCV
from src.services.market_data.market_data_service import MarketDataService

router = APIRouter(prefix="/market-data", tags=["Market Data Intelligence"])
market_service = MarketDataService()


class SyncRequest(BaseModel):
    """Payload to trigger data synchronization."""
    symbol: Optional[str] = None
    timeframe: str = "1d"
    lookback_days: int = 30
    sync_macro: bool = False


@router.get("/overview", summary="Multi-asset and macroeconomic environment snapshot")
async def get_market_overview(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Return consolidated quotes for reference assets across the 4 compartments and key macro metrics."""
    return await market_service.get_market_overview(db)


@router.get("/quote/{symbol}", summary="Latest price quote for a symbol")
async def get_latest_quote(
    symbol: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Retrieve the latest real-time/EOD price for an equity, ETF, or cryptocurrency."""
    quote = await market_service.get_latest_quote(db, symbol)
    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unable to fetch price quote for '{symbol}'"
        )
    return quote.model_dump()


@router.get("/history/{symbol}", summary="Historical OHLCV candlestick data")
async def get_historical_candles(
    symbol: str,
    timeframe: str = Query(default="1d", pattern="^(1m|1h|1d|1w)$"),
    limit: int = Query(default=60, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Fetch stored historical OHLCV candlesticks for an asset."""
    clean_sym = symbol.upper()
    asset_res = await db.execute(select(Asset).where(Asset.symbol == clean_sym))
    asset = asset_res.scalars().first()

    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset '{clean_sym}' not found in registry. Please sync it first."
        )

    stmt = (
        select(MarketDataOHLCV)
        .where(
            and_(
                MarketDataOHLCV.asset_id == asset.id,
                MarketDataOHLCV.timeframe == timeframe,
            )
        )
        .order_by(MarketDataOHLCV.timestamp.desc())
        .limit(limit)
    )
    res = await db.execute(stmt)
    rows = res.scalars().all()

    bars = [
        {
            "timestamp": r.timestamp.isoformat(),
            "open": float(r.open),
            "high": float(r.high),
            "low": float(r.low),
            "close": float(r.close),
            "volume": float(r.volume),
        }
        for r in reversed(rows)
    ]

    return {
        "symbol": clean_sym,
        "timeframe": timeframe,
        "count": len(bars),
        "bars": bars,
    }


@router.post("/sync", summary="Trigger data synchronization")
async def sync_market_data(
    req: SyncRequest,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Synchronize OHLCV historical bars for a symbol and/or update macroeconomic indicators."""
    result: Dict[str, Any] = {"status": "success"}

    if req.sync_macro:
        macro_count = await market_service.sync_macro_indicators(db)
        result["macro_indicators_synced"] = macro_count

    if req.symbol:
        bars_count = await market_service.sync_asset_bars(
            db=db,
            symbol=req.symbol,
            timeframe=req.timeframe,
            lookback_days=req.lookback_days,
        )
        result["symbol"] = req.symbol.upper()
        result["bars_synced"] = bars_count

    return result
