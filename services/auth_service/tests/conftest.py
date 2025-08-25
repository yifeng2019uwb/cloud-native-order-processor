"""
Auth Service Test Configuration

Sets up test environment variables and fixtures before any imports.
This prevents the common package from failing during import due to missing environment variables.
"""

import sys
import os
import pytest
from unittest.mock import MagicMock, patch

# Set environment variables BEFORE any imports that might need them
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

# Add auth service src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Add common package to path
common_path = os.path.join(
    os.path.dirname(__file__), "..", "..", "common", "src"
)
if os.path.exists(common_path):
    sys.path.insert(0, common_path)

# Add services root to path
services_root = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, services_root)


@pytest.fixture
def mock_token_manager():
    """Mock TokenManager for testing JWT validation."""
    with patch('src.controllers.validate.TokenManager') as mock_class:
        mock_instance = MagicMock()
        mock_class.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_request():
    """Mock FastAPI Request object."""
    mock_req = MagicMock()
    mock_req.url.path = "/test/path"
    mock_req.headers = {}
    return mock_req


@pytest.fixture
def mock_current_user():
    """Mock current user context."""
    return {
        "username": "testuser",
        "role": "customer",
        "is_authenticated": True
    }


@pytest.fixture
def mock_user_context():
    """Mock user context returned by TokenManager."""
    return {
        "username": "testuser",
        "role": "customer",
        "is_authenticated": True,
        "expires_at": "2025-12-31T23:59:59Z",
        "created_at": "2025-01-01T00:00:00Z",
        "metadata": {"algorithm": "HS256"}
    }
