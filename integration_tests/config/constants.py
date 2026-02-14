"""
Integration Tests Constants
External Black Box Testing - Integration tests only interact through Gateway
No internal Docker/K8s details exposed
"""
import os

# Timeouts
class Timeouts:
    DEFAULT = 10
    SHORT = 5
    LONG = 30

# HTTP Status Codes
class StatusCodes:
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500

# Headers
class Headers:
    CONTENT_TYPE_JSON = {"Content-Type": "application/json"}
    AUTHORIZATION_BEARER = "Bearer {}"

# External Service Configuration (Integration tests only see Gateway)
class ExternalServices:
    # Gateway is the only entry point for integration tests
    # Use environment variable or default to localhost for local testing
    GATEWAY_HOST = os.getenv("GATEWAY_HOST", "localhost")
    GATEWAY_PORT = int(os.getenv("GATEWAY_PORT", "8080"))
    GATEWAY_BASE_URL = f"http://{GATEWAY_HOST}:{GATEWAY_PORT}"

    # Frontend (for end-to-end tests if needed)
    FRONTEND_HOST = "localhost"
    FRONTEND_PORT = 3000
    FRONTEND_URL = f"http://{FRONTEND_HOST}:{FRONTEND_PORT}"

# API Endpoints (Gateway-based architecture)
class APIEndpoints:
    # Gateway Base
    GATEWAY_HEALTH = "/health"
    GATEWAY_API_BASE = "/api/v1"
    SERVICE_VERSION = "/api/v1"

    # Auth Service Endpoints
    AUTH_LOGIN = "/auth/login"
    AUTH_REGISTER = "/auth/register"
    AUTH_PROFILE = "/auth/profile"
    AUTH_LOGOUT = "/auth/logout"

    # Inventory Service Endpoints
    INVENTORY_ASSETS = "/inventory/assets"
    INVENTORY_ASSET_BY_ID = "/inventory/assets/{asset_id}"

    # Order Service Endpoints
    ORDERS_CREATE = "/orders"
    ORDERS_GET_BY_ID = "/orders/{order_id}"
    ORDERS_LIST = "/orders"
    PORTFOLIO_GET = "/portfolio"

    # Balance Service Endpoints
    BALANCE_GET = "/balance"
    BALANCE_DEPOSIT = "/balance/deposit"
    BALANCE_WITHDRAW = "/balance/withdraw"
    BALANCE_TRANSACTIONS = "/balance/transactions"

    # Asset Balance Service Endpoints
    GET_ASSET_BALANCE_BY_ID = "/balance/asset/{asset_id}"  # Get specific asset balance by ID
    GET_ASSET_TRANSACTIONS_BY_ID = "/assets/{asset_id}/transactions"  # Get asset transaction history

    # Insights Service Endpoints
    INSIGHTS_PORTFOLIO = "/insights/portfolio"

# Test Data Constants
class TestData:
    # User Test Data
    TEST_USERNAME = "testuser"
    TEST_EMAIL = "test@example.com"
    TEST_PASSWORD = "TestPassword123!"
    TEST_FIRST_NAME = "Test"
    TEST_LAST_NAME = "User"

    # Asset Test Data
    TEST_ASSET_ID = "BTC"
    TEST_ASSET_ID_2 = "ETH"

    # Order Test Data
    TEST_ORDER_TYPE = "market"
    TEST_ORDER_SIDE = "buy"
    TEST_ORDER_QUANTITY = "0.001"
    TEST_ORDER_PRICE = "50000.00"

# Test Categories
class TestCategories:
    SMOKE = "smoke"
    UNIT = "unit"
    INTEGRATION = "integration"
    END_TO_END = "end_to_end"
    PERFORMANCE = "performance"
    SECURITY = "security"

# Retry Configuration
class RetryConfig:
    MAX_ATTEMPTS = 3
    DELAY_BETWEEN_ATTEMPTS = 1  # seconds
    BACKOFF_MULTIPLIER = 2

# Performance Thresholds
class PerformanceThresholds:
    RESPONSE_TIME_FAST = 100    # milliseconds
    RESPONSE_TIME_NORMAL = 500  # milliseconds
    RESPONSE_TIME_SLOW = 2000   # milliseconds

# Integration Test Architecture
class Architecture:
    """
    Integration tests treat the system as an external black box:
    - Only interact through Gateway (port 8080)
    - No knowledge of internal Docker/K8s ports
    - No direct service access
    - Pure external consumer perspective
    """
    ENTRY_POINT = "Gateway only"
    INTERNAL_KNOWLEDGE = "None - Black box testing"
    SERVICE_ACCESS = "Through Gateway API only"
    PORT_KNOWLEDGE = "Only Gateway port 8080"