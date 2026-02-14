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
from constants import APIEndpoints as APIConstants

# User Service API Enum (Gateway Routes)
class UserAPI(Enum):
    ROOT = APIConstants.AUTH_PROFILE  # Gateway redirects to profile for authenticated users
    REGISTER = APIConstants.AUTH_REGISTER
    LOGIN = APIConstants.AUTH_LOGIN
    PROFILE = APIConstants.AUTH_PROFILE
    LOGOUT = APIConstants.AUTH_LOGOUT
    HEALTH = APIConstants.GATEWAY_HEALTH  # Gateway health endpoint (direct, not via /api/v1)
    BALANCE = APIConstants.BALANCE_GET
    BALANCE_DEPOSIT = APIConstants.BALANCE_DEPOSIT
    BALANCE_WITHDRAW = APIConstants.BALANCE_WITHDRAW
    BALANCE_TRANSACTIONS = APIConstants.BALANCE_TRANSACTIONS
    PORTFOLIO = APIConstants.PORTFOLIO_GET
    GET_ASSET_BALANCE_BY_ID = APIConstants.GET_ASSET_BALANCE_BY_ID
    INSIGHTS_PORTFOLIO = APIConstants.INSIGHTS_PORTFOLIO

# Inventory Service API Enum (Gateway Routes)
class InventoryAPI(Enum):
    ROOT = APIConstants.INVENTORY_ASSETS  # Gateway redirects to assets list
    ASSETS = APIConstants.INVENTORY_ASSETS
    ASSET_BY_ID = APIConstants.INVENTORY_ASSET_BY_ID
    HEALTH = APIConstants.GATEWAY_HEALTH  # Gateway health endpoint (direct, not via /api/v1)

# Order Service API Enum (Gateway Routes)
class OrderAPI(Enum):
    ROOT = APIConstants.ORDERS_LIST  # Gateway redirects to orders list
    ORDERS = APIConstants.ORDERS_LIST
    ORDER_BY_ID = APIConstants.ORDERS_GET_BY_ID
    CREATE_ORDER = APIConstants.ORDERS_CREATE
    GET_ASSET_TRANSACTIONS_BY_ID = APIConstants.GET_ASSET_TRANSACTIONS_BY_ID
    HEALTH = APIConstants.GATEWAY_HEALTH  # Gateway health endpoint (direct, not via /api/v1)

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