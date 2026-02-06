"""
Test configuration and fixtures for insights service
"""
import sys
import os
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from decimal import Decimal

# Mock environment variables before any imports
os.environ.setdefault('AWS_REGION', 'us-west-2')
os.environ.setdefault('USERS_TABLE', 'test-users-table')
os.environ.setdefault('ORDERS_TABLE', 'test-orders-table')
os.environ.setdefault('INVENTORY_TABLE', 'test-inventory-table')
os.environ.setdefault('ENVIRONMENT', 'test')
os.environ.setdefault('JWT_SECRET_KEY', 'test-jwt-secret-key-for-insights-service-tests-at-least-32-chars')
os.environ.setdefault('LOG_LEVEL', 'INFO')
os.environ.setdefault('SERVICE_PORT', '8004')
os.environ.setdefault('TESTING', 'true')
os.environ.setdefault('CI', 'true')

# Add common package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "common"))

# Add current service src to path
current_service_src = os.path.join(os.path.dirname(__file__), "..", "src")
sys.path.insert(0, current_service_src)

# Add services root to path
services_root = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, services_root)

# Import common entities after path setup
# Note: This requires the common package to be installed: pip install -e ../common
from common.data.entities.user import User
from common.data.entities.user.balance import Balance
from common.data.entities.asset.asset_balance import AssetBalance
from common.data.entities.inventory.asset import Asset
from common.data.entities.order.order import Order, OrderType, OrderStatus


@pytest.fixture(autouse=True)
def mock_environment_variables():
    """Ensure all tests use mock environment variables."""
    test_env_vars = {
        'AWS_REGION': 'us-west-2',
        'USERS_TABLE': 'test-users-table',
        'ORDERS_TABLE': 'test-orders-table',
        'INVENTORY_TABLE': 'test-inventory-table',
        'ENVIRONMENT': 'test',
        'JWT_SECRET_KEY': 'test-jwt-secret-key-for-insights-service-tests-at-least-32-chars',
        'LOG_LEVEL': 'INFO',
        'SERVICE_PORT': '8004',
        'TESTING': 'true',
        'CI': 'true',
    }

    original_env = {}
    for key, value in test_env_vars.items():
        if key in os.environ:
            original_env[key] = os.environ[key]
        os.environ[key] = value

    yield test_env_vars

    # Restore original environment variables
    for key in test_env_vars:
        if key in original_env:
            os.environ[key] = original_env[key]
        else:
            os.environ.pop(key, None)


@pytest.fixture
def mock_user():
    """Mock user entity"""
    return User(
        username="testuser",
        email="test@example.com",
        password="hashed_password",
        first_name="Test",
        last_name="User",
        created_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    )


@pytest.fixture
def mock_balance():
    """Mock balance entity"""
    return Balance(
        username="testuser",
        current_balance=Decimal("5000.00")
    )


@pytest.fixture
def mock_asset_balances():
    """Mock asset balances"""
    return [
        AssetBalance(
            username="testuser",
            asset_id="BTC",
            quantity=Decimal("0.15")
        ),
        AssetBalance(
            username="testuser",
            asset_id="ETH",
            quantity=Decimal("2.5")
        )
    ]


@pytest.fixture
def mock_assets():
    """Mock assets"""
    return {
        "BTC": Asset(
            asset_id="BTC",
            name="Bitcoin",
            category="major",
            amount=Decimal("1000"),
            price_usd=Decimal("45000"),
            is_active=True,
            current_price=Decimal("45000"),
            price_change_percentage_24h=Decimal("2.5")
        ),
        "ETH": Asset(
            asset_id="ETH",
            name="Ethereum",
            category="major",
            amount=Decimal("5000"),
            price_usd=Decimal("2500"),
            is_active=True,
            current_price=Decimal("2500"),
            price_change_percentage_24h=Decimal("-1.2")
        )
    }


@pytest.fixture
def mock_orders():
    """Mock orders"""
    return [
        Order(
            order_id="order-1",
            username="testuser",
            order_type=OrderType.MARKET_BUY,
            status=OrderStatus.COMPLETED,
            asset_id="BTC",
            quantity=Decimal("0.05"),
            price=Decimal("44000"),
            total_amount=Decimal("2200"),
            created_at=datetime(2026, 1, 30, 14, 0, 0, tzinfo=timezone.utc)
        )
    ]


@pytest.fixture
def mock_current_user():
    """Mock current user from JWT - returns object with .username for controller compatibility"""
    mock_user = MagicMock()
    mock_user.username = "testuser"
    mock_user.email = "test@example.com"
    return mock_user
