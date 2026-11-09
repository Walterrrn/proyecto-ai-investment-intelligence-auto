"""Asset catalogue model."""

from enum import Enum
from typing import Optional
from sqlalchemy import Boolean, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base, TimestampMixin


class AssetClass(str, Enum):
    """Broad asset classification."""
    EQUITY = "EQUITY"
    ETF = "ETF"
    CRYPTO = "CRYPTO"
    FIXED_INCOME = "FIXED_INCOME"
    COMMODITY = "COMMODITY"
    CASH = "CASH"


class AllocationBucket(str, Enum):
    """Portfolio allocation bucket."""
    LONG_TERM = "LONG_TERM"       # Core 50%
    TACTICAL = "TACTICAL"         # Satellite 15%
    CRYPTO = "CRYPTO"             # Asymmetric 10%
    LIQUIDITY = "LIQUIDITY"       # Defensive 25%


class Asset(Base, TimestampMixin):
    """Financial asset entity."""
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    isin: Mapped[Optional[str]] = mapped_column(String(12), unique=True, index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    asset_class: Mapped[str] = mapped_column(String(20), nullable=False)
    allocation_bucket: Mapped[str] = mapped_column(String(20), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="EUR", nullable=False)
    exchange: Mapped[str] = mapped_column(String(30), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    positions = relationship("PortfolioPosition", back_populates="asset", cascade="all, delete-orphan")
    signals = relationship("Signal", back_populates="asset", cascade="all, delete-orphan")
