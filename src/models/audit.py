"""Immutable decision audit trail model."""

from datetime import datetime, timezone
from sqlalchemy import DateTime, Integer, JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from src.models.base import Base


class DecisionAuditLog(Base):
    """Immutable audit record for all algorithmic decisions and risk validations."""
    __tablename__ = "decision_audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )
    engine: Mapped[str] = mapped_column(String(30), nullable=False)
    asset_symbol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    action_type: Mapped[str] = mapped_column(String(30), nullable=False)
    quantitative_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0.0)
    
    risk_check_passed: Mapped[bool] = mapped_column(nullable=False)
    risk_evaluation_details: Mapped[dict] = mapped_column(JSON, default=dict)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    outcome: Mapped[str] = mapped_column(String(50), nullable=False)
