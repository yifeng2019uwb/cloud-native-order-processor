"""
API Endpoints Configuration
Gateway-based routing for all API endpoints used in integration tests
"""
from enum import Enum
import sys
import os

# Add config directory to path for imports
sys.path.append(os.path.dirname(__file__))
from service_urls import USER_SERVICE_URL, INVENTORY_SERVICE_URL, ORDER_SERVICE_URL

# User Service API Enum (Gateway Routes)
class UserAPI(Enum):
    ROOT = '/auth/profile'  # Gateway redirects to profile for authenticated users
    REGISTER = '/auth/register'
    LOGIN = '/auth/login'
    PROFILE = '/auth/profile'
    LOGOUT = '/auth/logout'
    HEALTH = '/health'  # Gateway health endpoint (direct, not via /api/v1)
    BALANCE = '/balance'
    BALANCE_DEPOSIT = '/balance/deposit'
    BALANCE_WITHDRAW = '/balance/withdraw'
    BALANCE_TRANSACTIONS = '/balance/transactions'

# Inventory Service API Enum (Gateway Routes)
class InventoryAPI(Enum):
    ROOT = '/inventory/assets'  # Gateway redirects to assets list
    ASSETS = '/inventory/assets'
    ASSET_BY_ID = '/inventory/assets/{id}'
    HEALTH = '/health'  # Gateway health endpoint (direct, not via /api/v1)

# Order Service API Enum (Gateway Routes)
class OrderAPI(Enum):
    ROOT = '/orders'  # Gateway redirects to orders list
    ORDERS = '/orders'
    ORDER_BY_ID = '/orders/{id}'
    CREATE_ORDER = '/orders'
    PORTFOLIO = '/portfolio/{username}'
    ASSET_BALANCES = '/assets/balances'
    ASSET_BALANCE_BY_ID = '/assets/{asset_id}/balance'
    ASSET_TRANSACTIONS = '/assets/{asset_id}/transactions'
    HEALTH = '/health'  # Gateway health endpoint (direct, not via /api/v1)

class APIEndpoints:
    """Centralized API endpoints configuration"""

    @classmethod
    def get_user_endpoint(cls, api: UserAPI) -> str:
        """Get complete user service URL by API enum"""
        # Health endpoint uses gateway directly, others use service URL
        if api == UserAPI.HEALTH:
            from service_urls import GATEWAY_SERVICE_URL
            return f"{GATEWAY_SERVICE_URL}{api.value}"
        return f"{USER_SERVICE_URL}{api.value}"

    @classmethod
    def get_inventory_endpoint(cls, api: InventoryAPI, **kwargs) -> str:
        """Get complete inventory service URL by API enum with optional formatting"""
        endpoint = api.value
        if kwargs:
            endpoint = endpoint.format(**kwargs)
        # Health endpoint uses gateway directly, others use service URL
        if api == InventoryAPI.HEALTH:
            from service_urls import GATEWAY_SERVICE_URL
            return f"{GATEWAY_SERVICE_URL}{endpoint}"
        return f"{INVENTORY_SERVICE_URL}{endpoint}"

    @classmethod
    def get_order_endpoint(cls, api: OrderAPI, **kwargs) -> str:
        """Get complete order service URL by API enum with optional formatting"""
        endpoint = api.value
        if kwargs:
            endpoint = endpoint.format(**kwargs)
        # Health endpoint uses gateway directly, others use service URL
        if api == OrderAPI.HEALTH:
            from service_urls import GATEWAY_SERVICE_URL
            return f"{GATEWAY_SERVICE_URL}{endpoint}"
        return f"{ORDER_SERVICE_URL}{endpoint}"