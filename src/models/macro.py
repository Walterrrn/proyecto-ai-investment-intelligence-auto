"""Macroeconomic indicators time-series model."""

from datetime import date
from typing import Optional
from sqlalchemy import Date, Integer, Numeric, String, Index
from sqlalchemy.orm import Mapped, mapped_column
from src.models.base import Base, TimestampMixin


class MacroIndicator(Base, TimestampMixin):
    """Macroeconomic indicator observation from FRED or official statistical sources."""
    __tablename__ = "macro_indicators"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    series_id: Mapped[str] = mapped_column(String(30), index=True, nullable=False)  # e.g. 'FEDFUNDS', 'T10Y2Y', 'CPIAUCSL'
    period_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    value: Mapped[float] = mapped_column(Numeric(16, 4), nullable=False)
    units: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # e.g. 'Percent', 'Index 1982-1984=100'
    source: Mapped[str] = mapped_column(String(30), default="FRED", nullable=False)

    __table_args__ = (
        Index("ix_macro_series_period", "series_id", "period_date", unique=True),
    )
