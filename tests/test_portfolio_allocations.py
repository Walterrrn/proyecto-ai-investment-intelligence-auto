"""Portfolio allocation breakdown and rebalance calculations test."""

import pytest
from src.services.portfolio_service import PortfolioService
from src.models.asset import Asset, AssetClass, AllocationBucket
from src.models.portfolio import PortfolioPosition


@pytest.mark.asyncio
async def test_portfolio_default_simulation_allocation(db_session):
    """Test allocation calculation when no positions exist (100% liquidity available)."""
    service = PortfolioService(db_session)
    result = await service.get_allocation_breakdown()

    assert result["total_wealth_eur"] == 20000.00
    assert result["invested_equity_eur"] == 0.00
    assert result["liquidity_eur"] == 20000.00
    assert result["target_pct"]["LONG_TERM"] == 50.0
    assert result["target_pct"]["TACTICAL"] == 15.0
    assert result["target_pct"]["CRYPTO"] == 10.0
    assert result["target_pct"]["LIQUIDITY"] == 25.0


@pytest.mark.asyncio
async def test_portfolio_with_active_positions(db_session):
    """Test allocation calculation with real positions in the database."""
    # Seed sample assets
    asset_etf = Asset(
        symbol="VWCE",
        name="Vanguard FTSE All-World UCITS ETF",
        asset_class=AssetClass.ETF.value,
        allocation_bucket=AllocationBucket.LONG_TERM.value,
        currency="EUR",
        exchange="XETRA"
    )
    asset_crypto = Asset(
        symbol="BTC-EUR",
        name="Bitcoin",
        asset_class=AssetClass.CRYPTO.value,
        allocation_bucket=AllocationBucket.CRYPTO.value,
        currency="EUR",
        exchange="KRAKEN"
    )
    db_session.add_all([asset_etf, asset_crypto])
    await db_session.flush()

    # Seed positions
    # 50 shares of VWCE at 110 EUR = 5,500 EUR
    pos1 = PortfolioPosition(
        asset_id=asset_etf.id,
        broker="IBKR",
        allocation_bucket=AllocationBucket.LONG_TERM.value,
        quantity=50.0,
        avg_buy_price_eur=100.0,
        current_price_eur=110.0,
    )
    # 0.03 BTC at 60,000 EUR = 1,800 EUR
    pos2 = PortfolioPosition(
        asset_id=asset_crypto.id,
        broker="KRAKEN",
        allocation_bucket=AllocationBucket.CRYPTO.value,
        quantity=0.03,
        avg_buy_price_eur=55000.0,
        current_price_eur=60000.0,
    )
    db_session.add_all([pos1, pos2])
    await db_session.commit()

    service = PortfolioService(db_session)
    result = await service.get_allocation_breakdown()

    assert result["invested_equity_eur"] == 7300.00 # 5500 + 1800
    assert result["buckets_eur"]["LONG_TERM"] == 5500.00
    assert result["buckets_eur"]["CRYPTO"] == 1800.00
    assert result["total_wealth_eur"] == 20000.00
    assert result["liquidity_eur"] == 12700.00 # 20000 - 7300
