import pytest
from fastapi.testclient import TestClient

def test_app_import():
    """Test that the app can be imported"""
    from src.main import app
    assert app is not None
    assert hasattr(app, 'routes')

def test_app_has_required_routers():
    """Test that required routers are included"""
    from src.main import app

    # Check if assets router is included
    assets_routes = [route for route in app.routes if hasattr(route, 'path') and '/inventory/assets' in str(route.path)]
    assert len(assets_routes) > 0

    # Check if health router is included
    health_routes = [route for route in app.routes if hasattr(route, 'path') and '/health' in str(route.path)]
    assert len(health_routes) > 0

def test_app_title_and_version():
    """Test that app has correct title and version"""
    from src.main import app
    assert app.title == "Inventory Service"
    assert app.version == "1.0.0"

def test_root_endpoint():
    """Test root endpoint returns correct response"""
    from src.main import root

    response = root()
    assert response["service"] == "Inventory Service"
    assert response["version"] == "1.0.0"
    assert response["status"] == "running"
    assert "timestamp" in response
    assert "endpoints" in response