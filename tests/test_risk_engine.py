"""Risk Engine tests: position sizing, circuit breakers, and pre-trade checks."""

import pytest
from src.services.risk_service import RiskService


def test_position_sizing_calculation():
    """
    Test position sizing calculation:
    Capital: 20,000 EUR
    Max risk: 0.35% (70 EUR)
    Entry: 100 EUR, Stop Loss: 93 EUR (Risk per share = 7 EUR)
    Expected shares: floor(70 / 7) = 10 shares (Nominal: 1,000 EUR = 5% of portfolio)
    """
    risk_service = RiskService(current_total_wealth=20000.0)
    sizing = risk_service.calculate_position_sizing(
        entry_price=100.0,
        stop_loss_price=93.0,
        risk_pct=0.0035,
    )

    assert sizing["risk_amount_eur"] == 70.0
    assert sizing["risk_per_share_eur"] == 7.0
    assert sizing["recommended_shares"] == 10
    assert sizing["nominal_position_eur"] == 1000.0
    assert sizing["portfolio_allocation_pct"] == 5.0


def test_position_sizing_invalid_geometry():
    """Verify error when stop loss is equal or higher than entry price."""
    risk_service = RiskService(current_total_wealth=20000.0)
    with pytest.raises(ValueError):
        risk_service.calculate_position_sizing(entry_price=100.0, stop_loss_price=105.0)


def test_circuit_breaker_drawdown_halt():
    """Verify trading halt when portfolio drawdown reaches 10%."""
    risk_service = RiskService(current_total_wealth=20000.0)
    cb = risk_service.check_circuit_breakers(
        current_drawdown_pct=0.105, # 10.5% drawdown
        daily_loss_pct=0.005,
        weekly_loss_pct=0.015,
    )
    assert cb["halt_trading"] is True
    assert "Maximum drawdown limit hit" in cb["reason"]
    assert cb["severity"] == "CRITICAL"


def test_circuit_breaker_daily_loss_halt():
    """Verify trading halt when daily loss reaches 1.0%."""
    risk_service = RiskService(current_total_wealth=20000.0)
    cb = risk_service.check_circuit_breakers(
        current_drawdown_pct=0.03,
        daily_loss_pct=0.011, # 1.1% loss
        weekly_loss_pct=0.015,
    )
    assert cb["halt_trading"] is True
    assert "Daily loss limit reached" in cb["reason"]


def test_pre_trade_validation_passes():
    """Verify valid proposal passes sovereign risk checks."""
    risk_service = RiskService(current_total_wealth=20000.0)
    validation = risk_service.validate_proposal(
        asset_symbol="ASML",
        entry_price=800.0,
        stop_loss_price=760.0,
        current_open_risk_pct=0.005, # 0.5% open
        current_drawdown_pct=0.02,   # 2% drawdown
    )
    assert validation["approved"] is True
    assert validation["sizing"]["recommended_shares"] > 0


def test_pre_trade_validation_rejects_excess_aggregate_risk():
    """Verify rejection when open risk ceiling would be breached."""
    risk_service = RiskService(current_total_wealth=20000.0)
    validation = risk_service.validate_proposal(
        asset_symbol="ASML",
        entry_price=800.0,
        stop_loss_price=760.0,
        current_open_risk_pct=0.012, # 1.2% already open (+ 0.5% = 1.7% > 1.5% max)
        current_drawdown_pct=0.02,
    )
    assert validation["approved"] is False
    assert "Aggregate open risk limit exceeded" in validation["rejection_reason"]
