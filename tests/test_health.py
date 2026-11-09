"""Health check and root endpoint tests."""

import pytest


@pytest.mark.asyncio
async def test_root_endpoint(client):
    """Test root welcome endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Welcome" in data["message"]
    assert data["mode"] == "ANALYST_ONLY"


@pytest.mark.asyncio
async def test_health_endpoint(client):
    """Test health check and safety assertions."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["autonomy_mode"] == "ANALYST_ONLY"
    assert data["live_trading_enabled"] is False
