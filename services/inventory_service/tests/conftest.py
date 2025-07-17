import sys
import os
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from decimal import Decimal

# Add common package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))

# Add inventory-service src to path
inventory_service_src = os.path.join(
    os.path.dirname(__file__), "..", "src"
)
sys.path.insert(0, inventory_service_src)

# Add services root to path
services_root = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, services_root)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_db_connection():
    """Mock database connection for testing."""
    mock_conn = AsyncMock()
    mock_conn.fetchrow = AsyncMock()
    mock_conn.fetch = AsyncMock()
    mock_conn.execute = AsyncMock()
    mock_conn.transaction = AsyncMock()
    return mock_conn


@pytest.fixture
def sample_asset_data():
    """Sample asset data for testing."""
    return {
        "asset_id": "BTC",
        "name": "Bitcoin",
        "symbol": "BTC",
        "is_active": True,
        "current_price": Decimal("45000.00"),
        "market_cap": Decimal("850000000000"),
        "volume_24h": Decimal("25000000000"),
        "created_at": datetime(2024, 1, 1, 12, 0, 0),
        "updated_at": datetime(2024, 1, 1, 12, 0, 0),
    }