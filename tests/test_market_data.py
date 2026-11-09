"""Unit and integration tests for Market Intelligence collectors and endpoints."""

import pytest
from datetime import datetime, timezone, date
from unittest.mock import patch, MagicMock, AsyncMock
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.market_data.schemas import OHLCVBarDTO, QuoteDTO, MacroObservationDTO
from src.services.market_data.yahoo_collector import YahooFinanceCollector
from src.services.market_data.crypto_collector import CryptoDataCollector
from src.services.market_data.fred_collector import FredMacroCollector
from src.services.market_data.market_data_service import MarketDataService


@pytest.mark.asyncio
async def test_yahoo_collector_mocked():
    """Test YahooFinanceCollector parsing logic with mocked ticker."""
    collector = YahooFinanceCollector()

    mock_row = {
        "Open": 100.0,
        "High": 105.0,
        "Low": 99.0,
        "Close": 104.0,
        "Volume": 10000.0,
    }
    mock_df = MagicMock()
    mock_df.empty = False
    mock_df.iterrows.return_value = [
        (datetime(2026, 11, 1, 0, 0, tzinfo=timezone.utc), mock_row)
    ]

    with patch("yfinance.Ticker") as mock_ticker:
        mock_inst = MagicMock()
        mock_inst.history.return_value = mock_df
        mock_ticker.return_value = mock_inst

        bars = await collector.fetch_bars("URTH", timeframe="1d", lookback_days=5)

    assert len(bars) == 1
    assert bars[0].close == 104.0
    assert bars[0].volume == 10000.0


@pytest.mark.asyncio
async def test_crypto_collector_mocked():
    """Test CryptoDataCollector parsing logic with mocked CCXT response."""
    collector = CryptoDataCollector()

    # CCXT OHLCV format: [timestamp_ms, open, high, low, close, volume]
    mock_candles = [
        [1731110400000, 75000.0, 76500.0, 74200.0, 76000.0, 1500.0],
        [1731196800000, 76000.0, 77200.0, 75800.0, 77000.0, 1800.0],
    ]

    mock_exchange_inst = MagicMock()
    mock_exchange_inst.fetch_ohlcv.return_value = mock_candles

    with patch.object(collector, "_exchange_cls", return_value=mock_exchange_inst):
        bars = await collector.fetch_bars("BTC", timeframe="1d", lookback_days=2)

    assert len(bars) == 2
    assert bars[0].open == 75000.0
    assert bars[1].close == 77000.0


@pytest.mark.asyncio
async def test_fred_collector_fallback():
    """Test FredMacroCollector returns valid baseline data even with no API key."""
    collector = FredMacroCollector(api_key="")
    obs = await collector.fetch_series_observations("FEDFUNDS")

    assert len(obs) == 1
    assert obs[0].series_id == "FEDFUNDS"
    assert obs[0].value == 4.58


@pytest.mark.asyncio
async def test_market_data_service_db_sync(db_session: AsyncSession):
    """Test MarketDataService stores candles and macro observations into DB."""
    mock_bars = [
        OHLCVBarDTO(
            timestamp=datetime(2026, 11, 1, 0, 0, tzinfo=timezone.utc),
            open=100.0,
            high=102.0,
            low=99.0,
            close=101.5,
            volume=5000.0,
        ),
        OHLCVBarDTO(
            timestamp=datetime(2026, 11, 2, 0, 0, tzinfo=timezone.utc),
            open=101.5,
            high=103.0,
            low=101.0,
            close=102.8,
            volume=6200.0,
        ),
    ]

    mock_yahoo = MagicMock(spec=YahooFinanceCollector)
    mock_yahoo.fetch_bars = AsyncMock(return_value=mock_bars)

    service = MarketDataService(yahoo_collector=mock_yahoo)
    synced_count = await service.sync_asset_bars(
        db=db_session,
        symbol="URTH",
        timeframe="1d",
        lookback_days=5
    )

    assert synced_count == 2

    # Syncing again should update without throwing primary key duplicate error
    second_sync = await service.sync_asset_bars(
        db=db_session,
        symbol="URTH",
        timeframe="1d",
        lookback_days=5
    )
    assert second_sync == 2

    # Sync Macro
    macro_count = await service.sync_macro_indicators(db_session)
    assert macro_count == 4  # 4 core indicators


@pytest.mark.asyncio
async def test_api_market_data_endpoints(client: AsyncClient, db_session: AsyncSession):
    """Test FastAPI market-data REST endpoints."""
    # 1. Overview endpoint
    resp = await client.get("/api/v1/market-data/overview")
    assert resp.status_code == 200
    data = resp.json()
    assert "compartments_quotes" in data
    assert "macro_environment" in data
    assert "FEDFUNDS" in data["macro_environment"]

    # 2. Sync endpoint with macro
    sync_resp = await client.post(
        "/api/v1/market-data/sync",
        json={"sync_macro": True}
    )
    assert sync_resp.status_code == 200
    sync_data = sync_resp.json()
    assert sync_data["status"] == "success"
    assert sync_data["macro_indicators_synced"] >= 1

    # 3. History endpoint 404 for unknown asset
    hist_404 = await client.get("/api/v1/market-data/history/UNKNOWN_TICKER")
    assert hist_404.status_code == 404
