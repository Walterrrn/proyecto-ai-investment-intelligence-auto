"""Market Data and Quantitative Intelligence Service Package."""

from src.services.market_data.schemas import OHLCVBarDTO, QuoteDTO, MacroObservationDTO
from src.services.market_data.base import BaseMarketDataCollector
from src.services.market_data.yahoo_collector import YahooFinanceCollector
from src.services.market_data.crypto_collector import CryptoDataCollector
from src.services.market_data.fred_collector import FredMacroCollector
from src.services.market_data.market_data_service import MarketDataService

__all__ = [
    "OHLCVBarDTO",
    "QuoteDTO",
    "MacroObservationDTO",
    "BaseMarketDataCollector",
    "YahooFinanceCollector",
    "CryptoDataCollector",
    "FredMacroCollector",
    "MarketDataService",
]
