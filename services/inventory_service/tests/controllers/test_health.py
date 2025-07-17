import pytest

def test_health_endpoint_function_import():
    # Test that the function can be imported
    from inventory_service.src.controllers.health import health_check
    assert callable(health_check)

def test_controllers_init_import():
    import inventory_service.src.controllers.__init__