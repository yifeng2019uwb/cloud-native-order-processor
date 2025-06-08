import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch

from app import app


@pytest.mark.asyncio
async def test_root_routes_health_check():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}  # Adjust if your /health returns different data


@pytest.mark.asyncio
async def test_app_metadata():
    assert app.title == "Order Processing API"
    assert app.version == "1.0.0"
    assert app.description == "A cloud-native order processing system"


@pytest.mark.asyncio
@patch("app.db_manager")
async def test_shutdown_event(mock_db_manager):
    mock_db_manager.close_pool = AsyncMock()

    # Simulate shutdown event
    await app.router.lifespan_context(app).__aexit__(None, None, None)

    mock_db_manager.close_pool.assert_awaited_once()


@pytest.mark.asyncio
async def test_cors_middleware_headers():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.options("/health", headers={"Origin": "http://example.com"})
    assert "access-control-allow-origin" in response.headers
