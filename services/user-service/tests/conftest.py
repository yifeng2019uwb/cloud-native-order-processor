import sys
import os
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from decimal import Decimal

# Add common package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))

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
