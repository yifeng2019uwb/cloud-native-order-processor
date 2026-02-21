"""
Inventory Service API Info Enums - Only structural enums for type safety
"""
from enum import Enum

# =============================================================================
# API PREFIXES (constants for reuse)
# =============================================================================
API_INVENTORY_ROOT = ""  # Empty string for root router
API_INVENTORY_PREFIX = "/inventory"
API_ASSETS = "/assets"
API_ASSET_BY_ID = "/assets/{asset_id}"

# =============================================================================
# SERVICE METADATA ENUMS
# =============================================================================

class ServiceMetadata(str, Enum):
    """Service metadata - for type safety and validation"""
    NAME = "inventory-service"
    VERSION = "1.0.0"
    TITLE = "Inventory Service"
    DESCRIPTION = "A cloud-native inventory management service for crypto assets"
    STATUS_RUNNING = "running"


# =============================================================================
# API PATHS (full paths)
# =============================================================================

class ApiPaths(str, Enum):
    """API endpoint paths - full paths"""
    # System endpoints
    HEALTH = "/health"
    HEALTH_READY = "/health/ready"
    HEALTH_LIVE = "/health/live"
    METRICS = "/internal/metrics"
    DOCS = "/docs"
    REDOC = "/redoc"

    # Inventory endpoints
    ASSETS = "/inventory/assets"
    ASSET_BY_ID = "/inventory/assets/{asset_id}"


# =============================================================================
# API TAGS
# =============================================================================

class ApiTags(str, Enum):
    """API documentation tags - for type safety and validation"""
    INVENTORY = "inventory"
    HEALTH = "health"


# =============================================================================
# API RESPONSE KEYS
# =============================================================================

class ApiResponseKeys(str, Enum):
    """Standard keys used in FastAPI response definitions"""
    DESCRIPTION = "description"
    MODEL = "model"


# =============================================================================
# METRICS: path segments and operation names (no hardcoding in middleware)
# =============================================================================

class MetricOperation(str, Enum):
    """Operation names for asset and API-call metrics"""
    LIST_ASSETS = "list_assets"
    GET_ASSET_DETAIL = "get_asset_detail"
    CREATE_ASSET = "create_asset"
    UPDATE_ASSET = "update_asset"
    DELETE_ASSET = "delete_asset"


class MetricApiCall(str, Enum):
    """External API name for metrics"""
    COINGECKO = "coingecko"


# Path segment used to detect asset endpoints (must match ApiPaths.ASSETS)
PATH_SEGMENT_ASSETS = "/inventory/assets"
# Path segment to detect external API calls (e.g. /api/coingecko)
PATH_SEGMENT_API = "api"
URL_CONTAINS_COINGECKO = "coingecko"
# Slash count threshold: more than 3 slashes in path with ASSETS => get_asset_detail
ASSET_DETAIL_PATH_SLASH_COUNT = 3
