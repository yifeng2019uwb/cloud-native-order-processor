"""
Insights Service API Info Enums
"""
from enum import Enum

# =============================================================================
# SERVICE METADATA ENUMS
# =============================================================================

class ServiceMetadata(str, Enum):
    """Service metadata"""
    NAME = "insights-service"
    VERSION = "1.0.0"
    DESCRIPTION = "AI-powered portfolio insights service"
    STATUS_RUNNING = "running"


# =============================================================================
# API ENUMS
# =============================================================================

class ApiPaths(str, Enum):
    """API endpoint paths"""
    PORTFOLIO_INSIGHTS = "/insights/portfolio"

    # System endpoints
    METRICS = "/internal/metrics"
    HEALTH = "/health"
    DOCS = "/docs"
    REDOC = "/redoc"


class ApiTags(str, Enum):
    """API documentation tags"""
    INSIGHTS = "insights"
    HEALTH = "health"
