"""
User Service API Info Enums - Only structural enums for type safety
"""
from enum import Enum

# =============================================================================
# SERVICE METADATA ENUMS
# =============================================================================

class ServiceMetadata(str, Enum):
    """Service metadata - for type safety and validation"""
    NAME = "user-service"
    VERSION = "1.0.0"
    DESCRIPTION = "User authentication and balance management service"
    STATUS_RUNNING = "running"


# =============================================================================
# API ENUMS
# =============================================================================

class ApiPaths(str, Enum):
    """API endpoint paths - for type safety and validation"""
    # Auth endpoints
    LOGIN = "/auth/login"
    REGISTER = "/auth/register"
    LOGOUT = "/auth/logout"
    PROFILE = "/auth/profile"

    # Balance endpoints
    BALANCE = "/balance"
    DEPOSIT = "/balance/deposit"
    WITHDRAW = "/balance/withdraw"
    TRANSACTIONS = "/balance/transactions"
    ASSET_BALANCE = "/balance/asset/{asset_id}"

    # Portfolio endpoints
    PORTFOLIO = "/portfolio"

    # System endpoints
    HEALTH = "/health"
    METRICS = "/internal/metrics"
    DOCS = "/docs"
    REDOC = "/redoc"


class ApiTags(str, Enum):
    """API documentation tags - for type safety and validation"""
    AUTHENTICATION = "authentication"
    BALANCE = "balance"
    PORTFOLIO = "portfolio"
    ASSET_BALANCE = "asset balance"
    HEALTH = "health"


class ApiResponseKeys(str, Enum):
    """Standard keys used in FastAPI response definitions"""
    DESCRIPTION = "description"
    MODEL = "model"
