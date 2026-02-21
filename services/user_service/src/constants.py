"""
User Service Constants - Only constants (messages, field names, service metadata)
"""
# =============================================================================
# SUCCESS MESSAGES (Keep as constants - used in JSON responses)
# =============================================================================
MSG_SUCCESS_LOGIN = "Login successful"
MSG_SUCCESS_REGISTER = "User successfully registered"
MSG_SUCCESS_LOGOUT = "Logout successful"
MSG_SUCCESS_PROFILE_RETRIEVED = "User profile retrieved successfully"
MSG_SUCCESS_PROFILE_UPDATED = "Profile updated successfully"
MSG_SUCCESS_BALANCE_RETRIEVED = "Balance retrieved successfully"
MSG_SUCCESS_DEPOSIT = "Deposit successful"
MSG_SUCCESS_WITHDRAW = "Withdrawal successful"
MSG_SUCCESS_TRANSACTIONS_RETRIEVED = "Transactions retrieved successfully"
MSG_SUCCESS_PORTFOLIO_RETRIEVED = "Portfolio retrieved successfully"
MSG_SUCCESS_ASSET_BALANCE_RETRIEVED = "Asset balance retrieved successfully"

# =============================================================================
# ERROR MESSAGES (Keep as constants - used in JSON responses)
# =============================================================================
MSG_ERROR_USER_EXISTS = "User already exists"
MSG_ERROR_EMAIL_IN_USE = "Email already in use"
MSG_ERROR_INVALID_UPDATE_DATA = "Invalid update data"
MSG_ERROR_INSUFFICIENT_BALANCE = "Bad request - insufficient balance"
MSG_ERROR_INVALID_AMOUNT = "Bad request - invalid amount"
MSG_ERROR_USER_BALANCE_NOT_FOUND = "User balance not found"
MSG_ERROR_OPERATION_BUSY = "Operation is busy - try again"

# =============================================================================
# DAILY LIMITS (USD per user per calendar day - env overridable)
# =============================================================================
ENV_DAILY_DEPOSIT_LIMIT = "DAILY_DEPOSIT_LIMIT"
ENV_DAILY_WITHDRAW_LIMIT = "DAILY_WITHDRAW_LIMIT"
DEFAULT_DAILY_DEPOSIT_LIMIT = "10000"
DEFAULT_DAILY_WITHDRAW_LIMIT = "5000"

# =============================================================================
# METRICS RESULT LABELS (Prometheus metric label values: success / error)
# =============================================================================
METRICS_RESULT_SUCCESS = "success"
METRICS_RESULT_ERROR = "error"

# =============================================================================
# HTTP METHOD (for metrics path branching)
# =============================================================================
HTTP_METHOD_GET = "GET"
HTTP_METHOD_POST = "POST"

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
RESPONSE_FIELD_REGISTER = "register"
RESPONSE_FIELD_LOGIN = "login"
RESPONSE_FIELD_LOGOUT = "logout"
RESPONSE_FIELD_PROFILE = "profile"
RESPONSE_FIELD_BALANCE = "balance"
RESPONSE_FIELD_DEPOSIT = "deposit"
RESPONSE_FIELD_WITHDRAW = "withdraw"
RESPONSE_FIELD_TRANSACTIONS = "transactions"
RESPONSE_FIELD_PORTFOLIO = "portfolio"
RESPONSE_FIELD_ASSET_BALANCE = "asset_balance"
RESPONSE_FIELD_CNY_CLAIM = "cny_claim"
