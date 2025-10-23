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
os.environ.setdefault('JWT_SECRET_KEY', 'test-jwt-secret-key-for-user-service-tests-at-least-32-chars')
os.environ.setdefault('LOG_LEVEL', 'INFO')
os.environ.setdefault('PYTHONUNBUFFERED', '1')
os.environ.setdefault('TESTING', 'true')
os.environ.setdefault('CI', 'true')

# Add common package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))

# Add current service src to path
current_service_src = os.path.join(os.path.dirname(__file__), "..", "src")
sys.path.insert(0, current_service_src)

# Add order-service src to path for order-service tests
order_service_src = os.path.join(
    os.path.dirname(__file__), "..", "order-service", "src"
)
if os.path.exists(order_service_src):
    sys.path.insert(0, order_service_src)

# Add services root to path
services_root = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, services_root)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    if not loop.is_closed():
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
def mock_environment_variables():
    """Ensure all tests use mock environment variables."""
    # Set additional environment variables that might be needed
    test_env_vars = {
        'AWS_REGION': 'us-west-2',
        'USERS_TABLE': 'test-users-table',
        'ORDERS_TABLE': 'test-orders-table',
        'INVENTORY_TABLE': 'test-inventory-table',
        'ASSETS_TABLE': 'test-assets-table',
        'ENVIRONMENT': 'test',
        # JWT_SECRET_KEY and JWT_ALGORITHM removed - no longer needed for user service
        'LOG_LEVEL': 'INFO',
        'PYTHONUNBUFFERED': '1',
        'TESTING': 'true',
        'CI': 'true',
        'PORT': '8000',
        'HOST': '0.0.0.0',
        'SERVICE_ENVIRONMENT': 'test',
        'REDIS_URL': 'redis://localhost:6379',
        'REDIS_HOST': 'localhost',
        'REDIS_PORT': '6379',
        'REDIS_DB': '0',
        'REDIS_PASSWORD': '',
    }

    # Store original environment variables
    original_env = {}
    for key, value in test_env_vars.items():
        if key in os.environ:
            original_env[key] = os.environ[key]
        os.environ[key] = value

    yield test_env_vars

    # Restore original environment variables
    for key, value in test_env_vars.items():
        if key in original_env:
            os.environ[key] = original_env[key]
        else:
            os.environ.pop(key, None)


@pytest.fixture(autouse=True)
def mock_database_connection():
    """Mock database connection to prevent actual database calls during tests."""
    with patch('common.data.database.dynamodb_connection.get_dynamodb_manager') as mock_get_manager:
        # Mock the database manager
        mock_connection = AsyncMock()
        mock_users_table = MagicMock()
        mock_orders_table = MagicMock()
        mock_inventory_table = MagicMock()

        mock_connection.users_table = mock_users_table
        mock_connection.orders_table = mock_orders_table
        mock_connection.inventory_table = mock_inventory_table

        mock_manager = MagicMock()
        mock_manager.get_connection.return_value.__aenter__.return_value = mock_connection
        mock_manager.get_connection.return_value.__aexit__.return_value = None
        mock_get_manager.return_value = mock_manager

        yield mock_manager
