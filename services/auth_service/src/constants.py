"""
Auth Service Constants - Messages and configuration only
"""

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
RESPONSE_FIELD_VALIDATE = "validate"
RESPONSE_FIELD_METRICS = "metrics"

# =============================================================================
# TOKEN VALIDATION MESSAGES
# =============================================================================
class TokenValidationMessages:
    """Messages for token validation responses"""
    TOKEN_EXPIRED = "JWT token has expired"
    TOKEN_INVALID = "JWT token is invalid"
    VALIDATION_FAILED = "Token validation failed"
    VALIDATING_JWT = "Validating JWT"
    TOKEN_VALID = "Token valid"

# =============================================================================
# CORS CONFIGURATION
# =============================================================================
class CORSConfig:
    """CORS configuration constants"""
    ALLOW_ORIGINS = ["*"]  # Configure appropriately for production
    ALLOW_CREDENTIALS = True
    ALLOW_METHODS = ["*"]
    ALLOW_HEADERS = ["*"]

# CORS config dictionary for FastAPI middleware
CORS_CONFIG = {
    "allow_origins": CORSConfig.ALLOW_ORIGINS,
    "allow_credentials": CORSConfig.ALLOW_CREDENTIALS,
    "allow_methods": CORSConfig.ALLOW_METHODS,
    "allow_headers": CORSConfig.ALLOW_HEADERS
}

# =============================================================================
# SERVER CONFIGURATION
# =============================================================================
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000
SERVER_RELOAD = True

# =============================================================================
# METRICS STATUS LABELS
# =============================================================================
METRICS_STATUS_SUCCESS = "success"
METRICS_STATUS_ERROR = "error"