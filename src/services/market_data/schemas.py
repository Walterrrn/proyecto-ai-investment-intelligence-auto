"""Market data schemas and Data Transfer Objects (DTOs)."""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class OHLCVBarDTO(BaseModel):
    """Normalized OHLCV bar representation."""
    timestamp: datetime
    open: float = Field(gt=0)
    high: float = Field(gt=0)
    low: float = Field(gt=0)
    close: float = Field(gt=0)
    volume: float = Field(ge=0)
    vwap: Optional[float] = None


class QuoteDTO(BaseModel):
    """Latest price snapshot for an asset."""
    symbol: str
    price: float = Field(gt=0)
    change_24h_pct: Optional[float] = None
    volume_24h: Optional[float] = None
    timestamp: datetime


class MacroObservationDTO(BaseModel):
    """Single observation from a macroeconomic time series."""
    series_id: str
    period_date: date
    value: float
    units: Optional[str] = None
