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
