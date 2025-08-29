# Standard library imports
import asyncio
import os
import sys
from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

# Third-party imports
import pytest

# Mock environment variables before any imports that might need them
os.environ.setdefault('AWS_REGION', 'us-west-2')
os.environ.setdefault('USERS_TABLE', 'test-users-table')
os.environ.setdefault('ORDERS_TABLE', 'test-orders-table')
os.environ.setdefault('INVENTORY_TABLE', 'test-inventory-table')
os.environ.setdefault('ASSETS_TABLE', 'test-assets-table')
os.environ.setdefault('ENVIRONMENT', 'test')
os.environ.setdefault('JWT_SECRET', 'test-jwt-secret')
os.environ.setdefault('LOG_LEVEL', 'INFO')
os.environ.setdefault('PYTHONUNBUFFERED', '1')
os.environ.setdefault('TESTING', 'true')
os.environ.setdefault('CI', 'true')

# Add src directory to path for absolute imports (src.auth.security.password_manager)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Add current working directory to path for relative imports (..exceptions)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


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
def sample_order_data():
    """Sample order data for testing."""
    return {
        "order_id": "test-order-123",
        "customer_id": "customer-456",
        "customer_email": "test@example.com",
        "customer_name": "John Doe",
        "status": "pending",
        "total_amount": Decimal("99.99"),
        "currency": "USD",
        "shipping_address": {"street": "123 Main St", "city": "Test City"},
        "created_at": datetime(2024, 1, 1, 12, 0, 0),
        "updated_at": datetime(2024, 1, 1, 12, 0, 0),
    }


@pytest.fixture
def sample_product_data():
    """Sample product data for testing."""
    return {
        "product_id": "prod-123",
        "sku": "TEST-SKU-001",
        "name": "Test Product",
        "description": "A test product",
        "price": Decimal("29.99"),
        "category": "Electronics",
        "created_at": datetime(2024, 1, 1, 12, 0, 0),
        "updated_at": datetime(2024, 1, 1, 12, 0, 0),
    }


@pytest.fixture
def sample_inventory_data():
    """Sample inventory data for testing."""
    return {
        "product_id": "prod-123",
        "stock_quantity": 100,
        "reserved_quantity": 10,
        "min_stock_level": 5,
        "warehouse_location": "Warehouse A",
        "last_restocked_at": datetime(2024, 1, 1, 10, 0, 0),
        "created_at": datetime(2024, 1, 1, 12, 0, 0),
        "updated_at": datetime(2024, 1, 1, 12, 0, 0),
    }


@pytest.fixture(autouse=True)
def mock_database_connection():
    """Mock database connection to prevent actual database calls during tests."""
    with patch('src.data.database.dynamodb_connection.dynamodb_manager') as mock_manager:
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
