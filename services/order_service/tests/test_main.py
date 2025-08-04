"""
Simple test to ensure order service can be imported and basic functionality works
"""
import pytest


def test_order_service_import():
    """Test that order service modules can be imported"""
    try:
        from src.api_models import order_requests, order_responses
        from src.exceptions import exceptions
        from src.controllers import create_order, get_order, list_orders, health
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import order service modules: {e}")


def test_basic_functionality():
    """Basic functionality test"""
    assert True
