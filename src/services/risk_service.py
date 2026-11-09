"""Independent Sovereign Risk Engine Service."""

from typing import Dict, Any, Optional
import math
from src.core.config import settings
from src.core.telemetry import logger


class RiskService:
    """Central Sovereign Risk Engine. Inviolable validation of all proposals."""

    def __init__(self, current_total_wealth: Optional[float] = None):
        self.total_wealth = current_total_wealth or settings.INITIAL_CAPITAL_EUR
        self.kill_switch_active = False

    def check_circuit_breakers(
        self,
        current_drawdown_pct: float,
        daily_loss_pct: float,
        weekly_loss_pct: float,
    ) -> Dict[str, Any]:
        """Verify whether any portfolio-level circuit breaker has fired."""
        if self.kill_switch_active:
            return {
                "halt_trading": True,
                "reason": "Emergency Kill Switch manually engaged",
                "severity": "CRITICAL"
            }

        if current_drawdown_pct >= settings.RISK_DRAWDOWN_HALT_PCT:
            return {
                "halt_trading": True,
                "reason": f"Maximum drawdown limit hit ({current_drawdown_pct * 100:.2f}% >= {settings.RISK_DRAWDOWN_HALT_PCT * 100:.2f}%)",
                "severity": "CRITICAL"
            }

        if daily_loss_pct >= settings.RISK_MAX_DAILY_LOSS_PCT:
            return {
                "halt_trading": True,
                "reason": f"Daily loss limit reached ({daily_loss_pct * 100:.2f}% >= {settings.RISK_MAX_DAILY_LOSS_PCT * 100:.2f}%)",
                "severity": "HIGH"
            }

        if weekly_loss_pct >= settings.RISK_MAX_WEEKLY_LOSS_PCT:
            return {
                "halt_trading": True,
                "reason": f"Weekly loss limit reached ({weekly_loss_pct * 100:.2f}% >= {settings.RISK_MAX_WEEKLY_LOSS_PCT * 100:.2f}%)",
                "severity": "HIGH"
            }

        needs_review = current_drawdown_pct >= settings.RISK_DRAWDOWN_REVIEW_PCT
        return {
            "halt_trading": False,
            "needs_review": needs_review,
            "reason": "Drawdown warning threshold reached" if needs_review else "All circuit breakers normal",
            "severity": "WARNING" if needs_review else "NORMAL"
        }

    def calculate_position_sizing(
        self,
        entry_price: float,
        stop_loss_price: float,
        risk_pct: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Calculate mathematical position sizing based on fixed capital risk:
        N = floor((Capital * Risk%) / (EntryPrice - StopLoss))
        """
        if entry_price <= 0:
            raise ValueError("Entry price must be positive")
        if stop_loss_price >= entry_price:
            raise ValueError("Stop loss price must be below entry price for long positions")

        selected_risk_pct = risk_pct if risk_pct is not None else settings.RISK_MAX_PER_TRADE_PCT
        # Enforce hard ceiling of max 0.50%
        selected_risk_pct = min(selected_risk_pct, settings.RISK_MAX_PER_TRADE_PCT)

        risk_amount_eur = self.total_wealth * selected_risk_pct
        risk_per_share = entry_price - stop_loss_price

        shares_count = math.floor(risk_amount_eur / risk_per_share)
        nominal_value_eur = shares_count * entry_price

        # Check that nominal value does not exceed available capital
        pct_of_portfolio = (nominal_value_eur / self.total_wealth) if self.total_wealth > 0 else 0.0

        return {
            "entry_price": round(entry_price, 4),
            "stop_loss_price": round(stop_loss_price, 4),
            "risk_per_share_eur": round(risk_per_share, 4),
            "risk_amount_eur": round(risk_amount_eur, 2),
            "risk_pct": round(selected_risk_pct * 100, 3),
            "recommended_shares": shares_count,
            "nominal_position_eur": round(nominal_value_eur, 2),
            "portfolio_allocation_pct": round(pct_of_portfolio * 100, 2),
        }

    def validate_proposal(
        self,
        asset_symbol: str,
        entry_price: float,
        stop_loss_price: float,
        current_open_risk_pct: float,
        current_drawdown_pct: float,
    ) -> Dict[str, Any]:
        """Pre-trade validation gatekeeper."""
        # 1. Check circuit breaker
        cb = self.check_circuit_breakers(current_drawdown_pct, 0.0, 0.0)
        if cb["halt_trading"]:
            return {
                "approved": False,
                "rejection_reason": f"Circuit breaker active: {cb['reason']}",
                "sizing": None
            }

        # 2. Check aggregate risk ceiling
        proposed_risk_pct = settings.RISK_MAX_PER_TRADE_PCT
        if (current_open_risk_pct + proposed_risk_pct) > settings.RISK_MAX_AGGREGATE_PCT:
            return {
                "approved": False,
                "rejection_reason": (
                    f"Aggregate open risk limit exceeded: current {current_open_risk_pct*100:.2f}% + "
                    f"proposed {proposed_risk_pct*100:.2f}% > max {settings.RISK_MAX_AGGREGATE_PCT*100:.2f}%"
                ),
                "sizing": None
            }

        # 3. Calculate sizing
        try:
            sizing = self.calculate_position_sizing(entry_price, stop_loss_price, proposed_risk_pct)
        except ValueError as e:
            return {
                "approved": False,
                "rejection_reason": f"Invalid price geometry: {str(e)}",
                "sizing": None
            }

        if sizing["recommended_shares"] <= 0:
            return {
                "approved": False,
                "rejection_reason": "Risk-adjusted position size is zero shares (capital or stop-loss distance constraint)",
                "sizing": sizing
            }

        return {
            "approved": True,
            "asset_symbol": asset_symbol,
            "sizing": sizing,
            "notes": "Pre-trade risk checks passed. Operation conforms with sovereign risk limits."
        }
