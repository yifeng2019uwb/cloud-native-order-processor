"""
Order Service Constants - Messages only
"""

# =============================================================================
# SERVICE METADATA (Constants for backward compatibility)
# =============================================================================
SERVICE_NAME = "order-service"
SERVICE_VERSION = "1.0.0"
SERVICE_DESCRIPTION = "Order processing service"
SERVICE_STATUS_RUNNING = "running"


# =============================================================================
# RESPONSE FIELD NAMES (Keep as constants - used in JSON responses)
# =============================================================================
RESPONSE_FIELD_SERVICE = "service"
RESPONSE_FIELD_VERSION = "version"
RESPONSE_FIELD_STATUS = "status"
RESPONSE_FIELD_TIMESTAMP = "timestamp"
RESPONSE_FIELD_ENDPOINTS = "endpoints"
RESPONSE_FIELD_DOCS = "docs"
RESPONSE_FIELD_HEALTH = "health"
RESPONSE_FIELD_CREATE_ORDER = "create_order"
RESPONSE_FIELD_GET_ORDER = "get_order"
RESPONSE_FIELD_LIST_ORDERS = "list_orders"
RESPONSE_FIELD_ASSET_TRANSACTIONS = "asset_transactions"
RESPONSE_FIELD_METRICS = "metrics"

# =============================================================================
# MESSAGES
# =============================================================================

# Success messages
MSG_SUCCESS_ORDER_CREATED = "Order created successfully"
MSG_SUCCESS_MARKET_BUY_ORDER_CREATED = "Market Buy order created successfully"
MSG_SUCCESS_MARKET_SELL_ORDER_CREATED = "Market Sell order created successfully"
MSG_SUCCESS_ORDER_RETRIEVED = "Order retrieved successfully"
MSG_SUCCESS_ORDERS_LISTED = "Orders retrieved successfully"
MSG_SUCCESS_ASSET_TRANSACTIONS_RETRIEVED = "Asset transactions retrieved successfully"

# Error messages
MSG_ERROR_ORDER_NOT_FOUND = "Order not found"
MSG_ERROR_INVALID_ORDER_DATA = "Invalid order data"
MSG_ERROR_INSUFFICIENT_BALANCE = "Insufficient balance for order"
MSG_ERROR_ASSET_NOT_FOUND = "Asset not found"
MSG_ERROR_ORDER_ALREADY_EXISTS = "Order already exists"
MSG_ERROR_ORDER_VALIDATION_FAILED = "Order validation failed"
MSG_ERROR_ORDER_PROCESSING_FAILED = "Order processing failed"
MSG_ERROR_DATABASE_OPERATION_FAILED = "Database operation failed"
MSG_ERROR_LOCK_ACQUISITION_FAILED = "Unable to acquire lock for order processing"
MSG_ERROR_UNEXPECTED_ERROR = "An unexpected error occurred"

# =============================================================================
# COMMON STRINGS (Keep as constants - used in logging and headers)
# =============================================================================
USER_AGENT_HEADER = "user-agent"
UNKNOWN_VALUE = "unknown"