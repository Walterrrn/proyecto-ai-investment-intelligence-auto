"""Market data OHLCV model for time-series candles."""

from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, Integer, Numeric, String, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from src.models.base import Base


class MarketDataOHLCV(Base):
    """OHLCV candlestick data."""
    __tablename__ = "market_data_ohlcv"

    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    asset_id: Mapped[int] = mapped_column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), primary_key=True)
    timeframe: Mapped[str] = mapped_column(String(5), primary_key=True)  # '1m', '1h', '1d', '1w'
    
    open: Mapped[float] = mapped_column(Numeric(16, 6), nullable=False)
    high: Mapped[float] = mapped_column(Numeric(16, 6), nullable=False)
    low: Mapped[float] = mapped_column(Numeric(16, 6), nullable=False)
    close: Mapped[float] = mapped_column(Numeric(16, 6), nullable=False)
    volume: Mapped[float] = mapped_column(Numeric(24, 6), nullable=False)
    vwap: Mapped[Optional[float]] = mapped_column(Numeric(16, 6), nullable=True)

    __table_args__ = (
        Index("ix_market_data_asset_timeframe", "asset_id", "timeframe", "timestamp"),
    )
