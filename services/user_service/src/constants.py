"""
User Service Constants - Simplified for Personal Project
"""

# Service metadata
SERVICE_NAME = "user-service"
SERVICE_VERSION = "1.0.0"
SERVICE_DESCRIPTION = "User authentication and balance management service"

# Metrics endpoint
METRICS_ENDPOINT = "/internal/metrics"

# HTTP Status Codes
HTTP_STATUS_OK = 200
HTTP_STATUS_CREATED = 201
HTTP_STATUS_UNAUTHORIZED = 401
HTTP_STATUS_FORBIDDEN = 403
HTTP_STATUS_NOT_FOUND = 404
HTTP_STATUS_CONFLICT = 409
HTTP_STATUS_UNPROCESSABLE_ENTITY = 422
HTTP_STATUS_INTERNAL_SERVER_ERROR = 500

# API Endpoints
API_PREFIX_AUTH = "/auth"
API_PREFIX_ASSETS = "/balance"
API_ENDPOINT_BALANCE = "/balance"
API_ENDPOINT_PORTFOLIO = "/portfolio"
API_ENDPOINT_DEPOSIT = "/balance/deposit"
API_ENDPOINT_WITHDRAW = "/balance/withdraw"
API_ENDPOINT_TRANSACTIONS = "/balance/transactions"
API_ENDPOINT_ASSET_BALANCE = "/balance/asset/{asset_id}"

# API Tags
TAG_AUTHENTICATION = "authentication"
TAG_BALANCE = "balance"
TAG_PORTFOLIO = "portfolio"
TAG_ASSET_BALANCE = "asset balance"
TAG_HEALTH = "health"

# Request Headers
HEADER_REQUEST_ID = "X-Request-ID"
HEADER_USER_NAME = "X-User-Name"
HEADER_USER_ID = "X-User-ID"
HEADER_USER_ROLE = "X-User-Role"
HEADER_USER_AGENT = "user-agent"

# Default Values
DEFAULT_REQUEST_ID = "no-request-id"
DEFAULT_USERNAME = "testuser"
DEFAULT_USER_ID = "1"
DEFAULT_USER_ROLE = "customer"
DEFAULT_USER_AGENT = "unknown"

# Actions
ACTION_GET_ASSET_BALANCE = "get_asset_balance"
ACTION_VIEW_PORTFOLIO = "view_portfolio"

# Error Messages
ERROR_INTERNAL_SERVER = "Internal server error"
ERROR_VALIDATION = "Validation error"
ERROR_USER_EXISTS = "User already exists"
ERROR_USER_NOT_FOUND = "User not found"
ERROR_INSUFFICIENT_BALANCE = "Insufficient balance"
ERROR_INVALID_CREDENTIALS = "Invalid credentials"

# Success Messages
SUCCESS_PORTFOLIO_RETRIEVED = "Portfolio retrieved successfully"
SUCCESS_ASSET_BALANCE_RETRIEVED = "Asset balance retrieved successfully"

# Service Status
STATUS_RUNNING = "running"

# API Documentation Endpoints
ENDPOINT_DOCS = "/docs"
ENDPOINT_REDOC = "/redoc"
ENDPOINT_HEALTH = "/health"
ENDPOINT_REGISTER = "/auth/register"
ENDPOINT_LOGIN = "/auth/login"
ENDPOINT_PROFILE = "/auth/profile"
ENDPOINT_LOGOUT = "/auth/logout"

# Response Field Names
RESPONSE_SERVICE = "service"
RESPONSE_VERSION = "version"
RESPONSE_STATUS = "status"
RESPONSE_TIMESTAMP = "timestamp"
RESPONSE_ENDPOINTS = "endpoints"
RESPONSE_DOCS = "docs"
RESPONSE_HEALTH = "health"
RESPONSE_REGISTER = "register"
RESPONSE_LOGIN = "login"
RESPONSE_PROFILE = "profile"
RESPONSE_LOGOUT = "logout"
RESPONSE_BALANCE = "balance"
RESPONSE_DEPOSIT = "deposit"
RESPONSE_WITHDRAW = "withdraw"
RESPONSE_TRANSACTIONS = "transactions"
RESPONSE_PORTFOLIO = "portfolio"
RESPONSE_ASSET_BALANCE = "asset_balance"
