"""Yahoo Finance market data collector for equities and ETFs."""

import asyncio
from datetime import datetime, timezone
from typing import List, Optional
import yfinance as yf
from src.core.telemetry import logger
from src.services.market_data.base import BaseMarketDataCollector
from src.services.market_data.schemas import OHLCVBarDTO, QuoteDTO


class YahooFinanceCollector(BaseMarketDataCollector):
    """Fetches market data for stocks, ETFs, and indices via Yahoo Finance."""

    TIMEFRAME_MAP = {
        "1d": "1d",
        "1h": "1h",
        "1w": "1wk",
        "1m": "1mo",
    }

    async def fetch_bars(
        self,
        symbol: str,
        timeframe: str = "1d",
        lookback_days: int = 30
    ) -> List[OHLCVBarDTO]:
        """Fetch historical bars asynchronously using thread pool."""
        yf_interval = self.TIMEFRAME_MAP.get(timeframe, "1d")
        period = f"{max(lookback_days, 1)}d" if lookback_days <= 730 else "max"

        def _download():
            ticker = yf.Ticker(symbol)
            return ticker.history(period=period, interval=yf_interval)

        try:
            df = await asyncio.to_thread(_download)
        except Exception as exc:
            logger.error("yahoo_fetch_bars_error", symbol=symbol, error=str(exc))
            return []

        if df is None or df.empty:
            logger.warning("yahoo_no_data", symbol=symbol, timeframe=timeframe)
            return []

        bars: List[OHLCVBarDTO] = []
        for idx, row in df.iterrows():
            # Handle index datetime
            ts = idx.to_pydatetime() if hasattr(idx, "to_pydatetime") else idx
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            else:
                ts = ts.astimezone(timezone.utc)

            try:
                open_val = float(row["Open"])
                high_val = float(row["High"])
                low_val = float(row["Low"])
                close_val = float(row["Close"])
                volume_val = float(row["Volume"])

                # Sanity check
                if open_val <= 0 or high_val <= 0 or low_val <= 0 or close_val <= 0:
                    continue

                bars.append(
                    OHLCVBarDTO(
                        timestamp=ts,
                        open=open_val,
                        high=high_val,
                        low=low_val,
                        close=close_val,
                        volume=volume_val,
                    )
                )
            except (ValueError, KeyError):
                continue

        return bars

    async def fetch_latest_quote(self, symbol: str) -> Optional[QuoteDTO]:
        """Fetch current quote for symbol."""
        def _get_quote():
            ticker = yf.Ticker(symbol)
            fast = getattr(ticker, "fast_info", None)
            if fast:
                try:
                    price = float(fast.last_price)
                    prev_close = float(fast.previous_close) if hasattr(fast, "previous_close") else None
                    pct_change = ((price - prev_close) / prev_close * 100.0) if prev_close else None
                    return price, pct_change
                except Exception:
                    pass
            hist = ticker.history(period="2d", interval="1d")
            if not hist.empty:
                last_row = hist.iloc[-1]
                price = float(last_row["Close"])
                prev_close = float(hist.iloc[-2]["Close"]) if len(hist) > 1 else price
                pct_change = ((price - prev_close) / prev_close * 100.0) if prev_close else 0.0
                return price, pct_change
            return None, None

        try:
            price, pct = await asyncio.to_thread(_get_quote)
            if price is not None and price > 0:
                return QuoteDTO(
                    symbol=symbol,
                    price=price,
                    change_24h_pct=pct,
                    timestamp=datetime.now(timezone.utc),
                )
        except Exception as exc:
            logger.error("yahoo_fetch_quote_error", symbol=symbol, error=str(exc))

        return None
