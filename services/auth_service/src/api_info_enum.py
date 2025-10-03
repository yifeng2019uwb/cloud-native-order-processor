"""
Auth Service API Info Enums - Only structural enums for type safety
"""
from enum import Enum

# =============================================================================
# API PREFIXES (constants for reuse)
# =============================================================================
API_AUTH_ROOT = ""  # Empty string for root router
API_AUTH_PREFIX = "/internal/auth"

# =============================================================================
# SERVICE METADATA ENUMS
# =============================================================================

class ServiceMetadata(str, Enum):
    """Service metadata - for type safety and validation"""
    NAME = "auth-service"
    VERSION = "1.0.0"
    TITLE = "Auth Service"
    DESCRIPTION = "Independent JWT validation service"
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

    # Auth endpoints
    VALIDATE = "/internal/auth/validate"


# =============================================================================
# API TAGS
# =============================================================================

class ApiTags(str, Enum):
    """API documentation tags - for type safety and validation"""
    HEALTH = "health"
    INTERNAL = "internal"


# =============================================================================
# API RESPONSE KEYS
# =============================================================================

class ApiResponseKeys(str, Enum):
    """Standard keys used in FastAPI response definitions"""
    DESCRIPTION = "description"
    MODEL = "model"
