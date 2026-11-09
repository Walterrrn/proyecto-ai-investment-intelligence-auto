"""Crypto market data collector using CCXT (Kraken primary)."""

import asyncio
from datetime import datetime, timezone, timedelta
from typing import List, Optional
import ccxt
from src.core.telemetry import logger
from src.services.market_data.base import BaseMarketDataCollector
from src.services.market_data.schemas import OHLCVBarDTO, QuoteDTO


class CryptoDataCollector(BaseMarketDataCollector):
    """Fetches spot cryptocurrency market data via CCXT (Kraken / Binance)."""

    def __init__(self, primary_exchange: str = "kraken"):
        self.exchange_id = primary_exchange
        self._exchange_cls = getattr(ccxt, primary_exchange, ccxt.kraken)

    def _normalize_crypto_symbol(self, symbol: str) -> str:
        """Map generic symbol to standard CCXT pair (EUR preference)."""
        clean = symbol.upper().replace("-", "/").replace("_", "")
        if "/" not in clean:
            if clean in ("BTC", "ETH", "SOL"):
                return f"{clean}/EUR"
            return f"{clean}/EUR"
        return clean

    async def fetch_bars(
        self,
        symbol: str,
        timeframe: str = "1d",
        lookback_days: int = 30
    ) -> List[OHLCVBarDTO]:
        """Fetch crypto OHLCV candlestick data."""
        pair = self._normalize_crypto_symbol(symbol)
        since_dt = datetime.now(timezone.utc) - timedelta(days=lookback_days)
        since_ms = int(since_dt.timestamp() * 1000)

        def _fetch():
            exchange = self._exchange_cls({"enableRateLimit": True, "timeout": 10000})
            try:
                # ccxt timeframe standard: '1d', '1h', '1m', '1w'
                candles = exchange.fetch_ohlcv(pair, timeframe=timeframe, since=since_ms, limit=100)
                return candles
            except Exception as e:
                # If Kraken fails on pair, try with USDT
                if "EUR" in pair:
                    usdt_pair = pair.replace("/EUR", "/USDT")
                    try:
                        return exchange.fetch_ohlcv(usdt_pair, timeframe=timeframe, since=since_ms, limit=100)
                    except Exception:
                        pass
                raise e
            finally:
                exchange.close()

        try:
            raw_candles = await asyncio.to_thread(_fetch)
        except Exception as exc:
            logger.error("crypto_fetch_bars_error", symbol=symbol, pair=pair, error=str(exc))
            return []

        bars: List[OHLCVBarDTO] = []
        for candle in (raw_candles or []):
            try:
                # [timestamp_ms, open, high, low, close, volume]
                ts = datetime.fromtimestamp(candle[0] / 1000.0, tz=timezone.utc)
                bars.append(
                    OHLCVBarDTO(
                        timestamp=ts,
                        open=float(candle[1]),
                        high=float(candle[2]),
                        low=float(candle[3]),
                        close=float(candle[4]),
                        volume=float(candle[5]),
                    )
                )
            except (IndexError, ValueError):
                continue

        return bars

    async def fetch_latest_quote(self, symbol: str) -> Optional[QuoteDTO]:
        """Fetch current ticker quote."""
        pair = self._normalize_crypto_symbol(symbol)

        def _fetch_ticker():
            exchange = self._exchange_cls({"enableRateLimit": True, "timeout": 10000})
            try:
                return exchange.fetch_ticker(pair)
            except Exception:
                if "EUR" in pair:
                    return exchange.fetch_ticker(pair.replace("/EUR", "/USDT"))
                raise
            finally:
                exchange.close()

        try:
            ticker = await asyncio.to_thread(_fetch_ticker)
            price = float(ticker.get("last") or ticker.get("close") or 0.0)
            if price > 0:
                pct = float(ticker.get("percentage") or 0.0)
                vol = float(ticker.get("baseVolume") or 0.0)
                return QuoteDTO(
                    symbol=symbol,
                    price=price,
                    change_24h_pct=pct,
                    volume_24h=vol,
                    timestamp=datetime.now(timezone.utc),
                )
        except Exception as exc:
            logger.error("crypto_fetch_quote_error", symbol=symbol, pair=pair, error=str(exc))

        return None
