import pytest

def test_app_import():
    # Test that the app can be imported
    from inventory_service.src.main import app
    assert app is not None

def test_health_function_import():
    # Test that the health function can be imported
    from inventory_service.src.controllers.health import health_check
    assert callable(health_check)