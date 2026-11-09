"""Quantitative signals and proposed actions model."""

from enum import Enum
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base, TimestampMixin


class EngineSource(str, Enum):
    """Source engine producing the analysis signal."""
    INVESTMENT = "INVESTMENT"  # Long-term fundamental & quality
    TRADING = "TRADING"        # Tactical swing/momentum
    CRYPTO = "CRYPTO"          # Crypto module (BTC/ETH)


class SignalDirection(str, Enum):
    """Direction of the analytical signal."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class SignalStatus(str, Enum):
    """Lifecycle status of the generated signal."""
    NEW = "NEW"
    EVALUATED_BY_RISK = "EVALUATED_BY_RISK"
    APPROVED_FOR_SIMULATION = "APPROVED_FOR_SIMULATION"
    REJECTED_BY_RISK = "REJECTED_BY_RISK"
    EXPIRED = "EXPIRED"


class Signal(Base, TimestampMixin):
    """Quantitative signal entity."""
    __tablename__ = "signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    asset_id: Mapped[int] = mapped_column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    source_engine: Mapped[str] = mapped_column(String(20), nullable=False)
    direction: Mapped[str] = mapped_column(String(10), nullable=False)
    
    reference_price: Mapped[float] = mapped_column(Numeric(16, 4), nullable=False)
    entry_zone_min: Mapped[Optional[float]] = mapped_column(Numeric(16, 4), nullable=True)
    entry_zone_max: Mapped[Optional[float]] = mapped_column(Numeric(16, 4), nullable=True)
    stop_loss_price: Mapped[Optional[float]] = mapped_column(Numeric(16, 4), nullable=True)
    target_price: Mapped[Optional[float]] = mapped_column(Numeric(16, 4), nullable=True)
    
    confidence_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=50.0)  # 0 to 100
    time_horizon_days: Mapped[int] = mapped_column(Integer, default=30)
    status: Mapped[str] = mapped_column(String(30), default=SignalStatus.NEW.value, nullable=False)
    
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    invalidation_conditions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    asset = relationship("Asset", back_populates="signals")
