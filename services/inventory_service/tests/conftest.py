import sys
import os
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from decimal import Decimal

# Mock environment variables before any imports that might need them
os.environ.setdefault('AWS_REGION', 'us-west-2')
os.environ.setdefault('USERS_TABLE', 'test-users-table')
os.environ.setdefault('ORDERS_TABLE', 'test-orders-table')
os.environ.setdefault('INVENTORY_TABLE', 'test-inventory-table')
os.environ.setdefault('ASSETS_TABLE', 'test-assets-table')
os.environ.setdefault('ENVIRONMENT', 'test')
# JWT_SECRET removed - no longer needed for inventory service
os.environ.setdefault('LOG_LEVEL', 'INFO')
os.environ.setdefault('PYTHONUNBUFFERED', '1')
os.environ.setdefault('TESTING', 'true')
os.environ.setdefault('CI', 'true')

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


@pytest.fixture(autouse=True)
def mock_database_connection():
    """Mock database connection to prevent actual database calls during tests."""
    with patch('common.data.database.dynamodb_connection.dynamodb_manager') as mock_manager:
        # Mock the database manager
        mock_connection = AsyncMock()
        mock_users_table = MagicMock()
        mock_orders_table = MagicMock()
        mock_inventory_table = MagicMock()

        mock_connection.users_table = mock_users_table
        mock_connection.orders_table = mock_orders_table
        mock_connection.inventory_table = mock_inventory_table

        mock_manager.get_connection.return_value.__aenter__.return_value = mock_connection
        mock_manager.get_connection.return_value.__aexit__.return_value = None

        yield mock_manager