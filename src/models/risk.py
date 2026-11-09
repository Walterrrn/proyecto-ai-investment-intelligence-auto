"""Risk engine state, snapshots, and circuit breakers."""

from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column
from src.models.base import Base


class RiskSnapshot(Base):
    """Real-time risk telemetry record."""
    __tablename__ = "risk_snapshots"

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        primary_key=True,
        default=lambda: datetime.now(timezone.utc)
    )
    total_wealth_eur: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    daily_pnl_pct: Mapped[float] = mapped_column(Numeric(6, 4), nullable=False, default=0.0)
    weekly_pnl_pct: Mapped[float] = mapped_column(Numeric(6, 4), nullable=False, default=0.0)
    current_drawdown_pct: Mapped[float] = mapped_column(Numeric(6, 4), nullable=False, default=0.0)
    aggregate_open_risk_pct: Mapped[float] = mapped_column(Numeric(6, 4), nullable=False, default=0.0)
    
    circuit_breaker_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    kill_switch_engaged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    circuit_breaker_reason: Mapped[str] = mapped_column(String(200), default="", nullable=False)
