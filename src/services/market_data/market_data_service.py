"""Central Market Data Service orchestrating multi-asset feeds and persistence."""

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.telemetry import logger
from src.models.asset import Asset, AssetClass, AllocationBucket
from src.models.market_data import MarketDataOHLCV
from src.models.macro import MacroIndicator
from src.services.market_data.schemas import OHLCVBarDTO, QuoteDTO, MacroObservationDTO
from src.services.market_data.yahoo_collector import YahooFinanceCollector
from src.services.market_data.crypto_collector import CryptoDataCollector
from src.services.market_data.fred_collector import FredMacroCollector


class MarketDataService:
    """Orchestrates asset discovery, price feeds, macro indicators and DB persistence."""

    def __init__(
        self,
        yahoo_collector: Optional[YahooFinanceCollector] = None,
        crypto_collector: Optional[CryptoDataCollector] = None,
        fred_collector: Optional[FredMacroCollector] = None,
    ):
        self.yahoo = yahoo_collector or YahooFinanceCollector()
        self.crypto = crypto_collector or CryptoDataCollector()
        self.fred = fred_collector or FredMacroCollector()

    async def get_or_create_asset(
        self,
        db: AsyncSession,
        symbol: str,
        asset_class: str = AssetClass.EQUITY.value,
        allocation_bucket: str = AllocationBucket.LONG_TERM.value,
        name: Optional[str] = None,
        currency: str = "EUR",
        exchange: str = "SMART",
    ) -> Asset:
        """Find an asset by symbol or register a new one."""
        clean_symbol = symbol.upper()
        stmt = select(Asset).where(Asset.symbol == clean_symbol)
        result = await db.execute(stmt)
        asset = result.scalars().first()

        if not asset:
            # Auto-infer asset class and bucket if obvious
            if clean_symbol in ("BTC", "ETH", "SOL", "BTC/EUR", "ETH/EUR"):
                asset_class = AssetClass.CRYPTO.value
                allocation_bucket = AllocationBucket.CRYPTO.value
                exchange = "KRAKEN"
            elif clean_symbol in ("XEON.DE", "CSH2.PA", "EUR"):
                asset_class = AssetClass.CASH.value
                allocation_bucket = AllocationBucket.LIQUIDITY.value

            asset = Asset(
                symbol=clean_symbol,
                name=name or f"Asset {clean_symbol}",
                asset_class=asset_class,
                allocation_bucket=allocation_bucket,
                currency=currency,
                exchange=exchange,
                is_active=True,
            )
            db.add(asset)
            await db.commit()
            await db.refresh(asset)
            logger.info("asset_registered", symbol=clean_symbol, asset_class=asset_class)

        return asset

    async def sync_asset_bars(
        self,
        db: AsyncSession,
        symbol: str,
        timeframe: str = "1d",
        lookback_days: int = 30
    ) -> int:
        """Fetch bars from the appropriate collector and persist to database."""
        asset = await self.get_or_create_asset(db, symbol)

        # Select collector based on asset class
        if asset.asset_class == AssetClass.CRYPTO.value or symbol.upper() in ("BTC", "ETH", "BTC/EUR", "ETH/EUR"):
            bars: List[OHLCVBarDTO] = await self.crypto.fetch_bars(symbol, timeframe, lookback_days)
        else:
            bars: List[OHLCVBarDTO] = await self.yahoo.fetch_bars(symbol, timeframe, lookback_days)

        if not bars:
            logger.warning("sync_bars_empty", symbol=symbol, timeframe=timeframe)
            return 0

        saved_count = 0
        for bar in bars:
            # Check if bar already exists
            stmt = select(MarketDataOHLCV).where(
                and_(
                    MarketDataOHLCV.asset_id == asset.id,
                    MarketDataOHLCV.timeframe == timeframe,
                    MarketDataOHLCV.timestamp == bar.timestamp,
                )
            )
            res = await db.execute(stmt)
            existing = res.scalars().first()

            if existing:
                # Update existing record
                existing.open = bar.open
                existing.high = bar.high
                existing.low = bar.low
                existing.close = bar.close
                existing.volume = bar.volume
            else:
                new_bar = MarketDataOHLCV(
                    asset_id=asset.id,
                    timestamp=bar.timestamp,
                    timeframe=timeframe,
                    open=bar.open,
                    high=bar.high,
                    low=bar.low,
                    close=bar.close,
                    volume=bar.volume,
                )
                db.add(new_bar)
                saved_count += 1

        await db.commit()
        logger.info("sync_bars_success", symbol=symbol, bars_received=len(bars), new_saved=saved_count)
        return len(bars)

    async def get_latest_quote(
        self,
        db: AsyncSession,
        symbol: str
    ) -> Optional[QuoteDTO]:
        """Fetch latest quote for an asset."""
        asset = await self.get_or_create_asset(db, symbol)
        if asset.asset_class == AssetClass.CRYPTO.value or symbol.upper() in ("BTC", "ETH"):
            return await self.crypto.fetch_latest_quote(symbol)
        return await self.yahoo.fetch_latest_quote(symbol)

    async def sync_macro_indicators(self, db: AsyncSession) -> int:
        """Fetch and persist latest macroeconomic observations."""
        observations = await self.fred.fetch_core_macro_snapshot()
        saved = 0

        for obs in observations:
            stmt = select(MacroIndicator).where(
                and_(
                    MacroIndicator.series_id == obs.series_id,
                    MacroIndicator.period_date == obs.period_date,
                )
            )
            res = await db.execute(stmt)
            existing = res.scalars().first()

            if existing:
                existing.value = obs.value
                existing.units = obs.units
            else:
                rec = MacroIndicator(
                    series_id=obs.series_id,
                    period_date=obs.period_date,
                    value=obs.value,
                    units=obs.units,
                    source="FRED",
                )
                db.add(rec)
                saved += 1

        await db.commit()
        logger.info("sync_macro_success", count=len(observations), new_saved=saved)
        return len(observations)

    async def get_market_overview(self, db: AsyncSession) -> Dict[str, Any]:
        """Consolidate high-level market intelligence summary across all 4 compartments."""
        # Key reference symbols
        ref_symbols = {
            "core": "URTH",        # MSCI World ETF
            "tactical": "QQQ",     # Nasdaq 100 ETF (Momentum / Growth)
            "crypto": "BTC",       # Bitcoin
            "liquidity": "XEON.DE" # Overnight Euro liquidity ETF
        }

        quotes: Dict[str, Any] = {}
        for bucket, sym in ref_symbols.items():
            try:
                q = await self.get_latest_quote(db, sym)
                if q:
                    quotes[bucket] = {
                        "symbol": q.symbol,
                        "price": q.price,
                        "change_24h_pct": round(q.change_24h_pct, 2) if q.change_24h_pct is not None else 0.0,
                        "timestamp": q.timestamp.isoformat(),
                    }
                else:
                    quotes[bucket] = {"symbol": sym, "status": "unavailable"}
            except Exception as e:
                quotes[bucket] = {"symbol": sym, "error": str(e)}

        # Fetch latest macro indicators
        macro_stmt = select(MacroIndicator).order_by(MacroIndicator.period_date.desc()).limit(10)
        m_res = await db.execute(macro_stmt)
        macro_rows = m_res.scalars().all()

        macro_data: Dict[str, Any] = {}
        for m in macro_rows:
            if m.series_id not in macro_data:
                macro_data[m.series_id] = {
                    "value": float(m.value),
                    "date": m.period_date.isoformat(),
                    "units": m.units,
                }

        # If DB had no macro, get fallback baseline
        if not macro_data:
            snapshot = await self.fred.fetch_core_macro_snapshot()
            for obs in snapshot:
                macro_data[obs.series_id] = {
                    "value": obs.value,
                    "date": obs.period_date.isoformat(),
                    "units": obs.units,
                }

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "compartments_quotes": quotes,
            "macro_environment": macro_data,
        }
