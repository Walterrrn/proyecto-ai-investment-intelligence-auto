"""Base interface for market data collectors."""

from abc import ABC, abstractmethod
from typing import List, Optional
from src.services.market_data.schemas import OHLCVBarDTO, QuoteDTO


class BaseMarketDataCollector(ABC):
    """Abstract interface defining the contract for all market data connectors."""

    @abstractmethod
    async def fetch_bars(
        self,
        symbol: str,
        timeframe: str = "1d",
        lookback_days: int = 30
    ) -> List[OHLCVBarDTO]:
        """Fetch historical candlestick bars for a given symbol."""
        pass

    @abstractmethod
    async def fetch_latest_quote(self, symbol: str) -> Optional[QuoteDTO]:
        """Fetch the latest real-time or end-of-day price quote."""
        pass
