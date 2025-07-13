"""
Service URLs for Integration Tests
Simple configuration for FastAPI service URLs
"""
import os

def get_user_service_url() -> str:
    """Get User Service URL"""
    # Try environment variable first
    env_url = os.getenv('USER_SERVICE_URL')
    if env_url:
        return env_url

    # Default to localhost
    return "http://localhost:8000"

def get_inventory_service_url() -> str:
    """Get Inventory Service URL"""
    # Try environment variable first
    env_url = os.getenv('INVENTORY_SERVICE_URL')
    if env_url:
        return env_url

    # Default to localhost
    return "http://localhost:8001"

# Service URLs
USER_SERVICE_URL = get_user_service_url()
INVENTORY_SERVICE_URL = get_inventory_service_url()