"""
Order Service API Info Enums - Only structural enums for type safety
"""
from enum import Enum

# =============================================================================
# API PREFIXES (constants for reuse)
# =============================================================================
API_ORDERS_ROOT = "/"
API_ORDER_BY_ID = "/{order_id}"
API_PREFIX_ORDERS = "/orders"
API_PREFIX_ASSETS = "/assets"
API_ASSET_TRANSACTIONS = "/{asset_id}/transactions"

# =============================================================================
# SERVICE METADATA ENUMS
# =============================================================================

class ServiceMetadata(str, Enum):
    """Service metadata - for type safety and validation"""
    NAME = "order-service"
    VERSION = "1.0.0"
    TITLE = "Order Service"
    DESCRIPTION = "A cloud-native order processing service"
    STATUS_RUNNING = "running"


# =============================================================================
# API PATHS (full paths)
# =============================================================================

class ApiPaths(str, Enum):
    """API endpoint paths - full paths"""
    # System endpoints
    HEALTH = "/health"
    METRICS = "/internal/metrics"
    DOCS = "/docs"
    REDOC = "/redoc"

    # Order endpoints
    ORDERS = "/orders"
    ORDER_BY_ID = "/orders/{order_id}"

    # Asset endpoints
    ASSETS = "/assets"
    ASSET_BY_ID = "/assets/{asset_id}"
    ASSET_TRANSACTIONS = "/assets/{asset_id}/transactions"


class ApiTags(str, Enum):
    """API documentation tags - for type safety and validation"""
    ORDERS = "orders"
    ASSET_TRANSACTIONS = "asset transactions"
    HEALTH = "health"


class ApiResponseKeys(str, Enum):
    """Standard keys used in FastAPI response definitions"""
    DESCRIPTION = "description"
    MODEL = "model"
