"""Configuration and safety settings tests."""

from src.core.config import settings, AutonomyMode


def test_autonomy_mode_default():
    """Verify default autonomy is strictly ANALYST_ONLY."""
    assert settings.AUTONOMY_MODE == AutonomyMode.ANALYST_ONLY


def test_leverage_is_disabled():
    """Verify leverage is strictly disabled in configuration."""
    assert settings.LEVERAGE_ALLOWED is False


def test_portfolio_allocation_sum():
    """Verify default allocation scenario sums up to 100%."""
    total = (
        settings.ALLOCATION_LONG_TERM_PCT
        + settings.ALLOCATION_TACTICAL_PCT
        + settings.ALLOCATION_CRYPTO_PCT
        + settings.ALLOCATION_LIQUIDITY_PCT
    )
    assert abs(total - 1.0) < 0.0001
    assert settings.ALLOCATION_LONG_TERM_PCT == 0.50
    assert settings.ALLOCATION_TACTICAL_PCT == 0.15
    assert settings.ALLOCATION_CRYPTO_PCT == 0.10
    assert settings.ALLOCATION_LIQUIDITY_PCT == 0.25


def test_risk_limits_bounds():
    """Verify risk bounds are within prudent investor limits."""
    assert settings.RISK_MAX_PER_TRADE_PCT <= 0.0050  # Max 0.50%
    assert settings.RISK_MAX_AGGREGATE_PCT <= 0.0150  # Max 1.50%
    assert settings.RISK_MAX_DAILY_LOSS_PCT <= 0.0100 # Max 1.00%
    assert settings.RISK_DRAWDOWN_REVIEW_PCT == 0.0800 # 8%
    assert settings.RISK_DRAWDOWN_HALT_PCT == 0.1000   # 10%
