"""Portfolio positions and snapshot models."""

from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base, TimestampMixin


class PortfolioPosition(Base, TimestampMixin):
    """Current holding position in a portfolio."""
    __tablename__ = "portfolio_positions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    asset_id: Mapped[int] = mapped_column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    broker: Mapped[str] = mapped_column(String(30), default="IBKR", nullable=False)
    allocation_bucket: Mapped[str] = mapped_column(String(20), nullable=False)
    
    quantity: Mapped[float] = mapped_column(Numeric(18, 8), nullable=False, default=0.0)
    avg_buy_price_eur: Mapped[float] = mapped_column(Numeric(16, 4), nullable=False, default=0.0)
    current_price_eur: Mapped[float] = mapped_column(Numeric(16, 4), nullable=False, default=0.0)
    
    # Navigation property
    asset = relationship("Asset", back_populates="positions")

    @property
    def market_value_eur(self) -> float:
        """Calculate market value in EUR."""
        return float(self.quantity) * float(self.current_price_eur)

    @property
    def unrealized_pnl_eur(self) -> float:
        """Calculate unrealized PnL in EUR."""
        return float(self.quantity) * (float(self.current_price_eur) - float(self.avg_buy_price_eur))

    @property
    def unrealized_pnl_pct(self) -> float:
        """Calculate unrealized PnL percentage."""
        if float(self.avg_buy_price_eur) == 0:
            return 0.0
        return ((float(self.current_price_eur) - float(self.avg_buy_price_eur)) / float(self.avg_buy_price_eur)) * 100.0


class PortfolioSnapshot(Base):
    """Historical telemetry snapshot of total portfolio equity and allocations."""
    __tablename__ = "portfolio_snapshots"

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        primary_key=True,
        default=lambda: datetime.now(timezone.utc)
    )
    total_wealth_eur: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    invested_equity_eur: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    liquidity_eur: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    long_term_equity_eur: Mapped[float] = mapped_column(Numeric(14, 2), default=0.0)
    tactical_equity_eur: Mapped[float] = mapped_column(Numeric(14, 2), default=0.0)
    crypto_equity_eur: Mapped[float] = mapped_column(Numeric(14, 2), default=0.0)
