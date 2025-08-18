"""
API Endpoints Configuration
Centralized configuration for all API endpoints used in integration tests
"""
from enum import Enum
import sys
import os

# Add config directory to path for imports
sys.path.append(os.path.dirname(__file__))
from service_urls import USER_SERVICE_URL, INVENTORY_SERVICE_URL

# User Service API Enum
class UserAPI(Enum):
    ROOT = '/'
    REGISTER = '/auth/register'
    LOGIN = '/auth/login'
    PROFILE = '/auth/profile'
    LOGOUT = '/auth/logout'
    HEALTH = '/health'

# Inventory Service API Enum
class InventoryAPI(Enum):
    ROOT = '/'
    ASSETS = '/inventory/assets'
    ASSET_BY_ID = '/inventory/assets/{id}'
    HEALTH = '/health'

class APIEndpoints:
    """Centralized API endpoints configuration"""

    @classmethod
    def get_user_endpoint(cls, api: UserAPI) -> str:
        """Get complete user service URL by API enum"""
        return f"{USER_SERVICE_URL}{api.value}"

    @classmethod
    def get_inventory_endpoint(cls, api: InventoryAPI, **kwargs) -> str:
        """Get complete inventory service URL by API enum with optional formatting"""
        endpoint = api.value
        if kwargs:
            endpoint = endpoint.format(**kwargs)
        return f"{INVENTORY_SERVICE_URL}{endpoint}"