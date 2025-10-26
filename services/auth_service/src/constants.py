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
CORS_CONFIG = {
    "allow_origins": ["*"],  # Configure appropriately for production
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"]
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