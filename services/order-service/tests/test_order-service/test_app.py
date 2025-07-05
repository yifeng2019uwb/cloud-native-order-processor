import pytest
# from httpx import AsyncClient
from unittest.mock import AsyncMock, patch

from app import app, shutdown_event


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
async def test_shutdown_event():
    with patch("app.logger") as mock_logger:
        with patch("builtins.__import__", side_effect=lambda name, *args: None if name == "database" else __import__(name, *args)):
            # Call the shutdown function directly
            await shutdown_event()

            # Verify that shutdown was logged
            mock_logger.info.assert_called_with("Order Service shutting down...")

@pytest.mark.asyncio
async def test_cors_middleware_headers():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.options("/health", headers={"Origin": "http://example.com"})
    assert "access-control-allow-origin" in response.headers
