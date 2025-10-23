"""
Auth Service Metrics - Simplified for Personal Project
"""

import time
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
from common.shared.logging import BaseLogger, Loggers, LogActions
from common.shared.constants.api_constants import HTTPStatus
from api_info_enum import ServiceMetadata

logger = BaseLogger(Loggers.AUTH)

# =============================================================================
# METRICS CONSTANTS (Local constants for this service)
# =============================================================================

# Service info constants
SERVICE_INFO_NAME = "auth_service_info"
SERVICE_INFO_DESCRIPTION = "Auth service information"

# Metrics names
AUTH_REQUESTS_TOTAL = "auth_requests_total"
JWT_VALIDATIONS_TOTAL = "jwt_validations_total"
REQUEST_DURATION = "auth_request_duration_seconds"
SERVICE_UPTIME = "auth_service_uptime_seconds"

# Metrics descriptions
MSG_TOTAL_AUTH_REQUESTS = "Total auth requests"
MSG_TOTAL_JWT_VALIDATIONS = "Total JWT validations"
MSG_REQUEST_DURATION = "Request duration"
MSG_SERVICE_UPTIME = "Service uptime"

# Metrics labels
LABEL_STATUS = "status"
LABEL_RESULT = "result"

# Response constants
CACHE_CONTROL_HEADER = "Cache-Control"
NO_CACHE_VALUE = "no-cache"
ERROR_CONTENT = "# Error\n"

# ========================================
# SIMPLE METRICS
# ========================================

# Service info
service_info = Info(SERVICE_INFO_NAME, SERVICE_INFO_DESCRIPTION)
service_info.info({'version': ServiceMetadata.VERSION.value, 'service': ServiceMetadata.NAME.value})

# Core counters
auth_requests_total = Counter(AUTH_REQUESTS_TOTAL, MSG_TOTAL_AUTH_REQUESTS, [LABEL_STATUS])
jwt_validations_total = Counter(JWT_VALIDATIONS_TOTAL, MSG_TOTAL_JWT_VALIDATIONS, [LABEL_RESULT])

# Simple histogram
request_duration = Histogram(REQUEST_DURATION, MSG_REQUEST_DURATION, [LABEL_STATUS])

# Uptime
service_uptime = Gauge(SERVICE_UPTIME, MSG_SERVICE_UPTIME)
_start_time = time.time()

# ========================================
# SIMPLE COLLECTOR
# ========================================

class SimpleMetricsCollector:
    """Simple metrics collector"""

    def record_jwt_validation(self, result: str, duration: float = None):
        """Record JWT validation"""
        jwt_validations_total.labels(result=result).inc()
        if duration:
            request_duration.labels(status=result).observe(duration)

    def record_request(self, status: str, duration: float = None):
        """Record request"""
        auth_requests_total.labels(status=status).inc()
        if duration:
            request_duration.labels(status=status).observe(duration)

    def get_metrics(self) -> bytes:
        """Get metrics"""
        service_uptime.set(time.time() - _start_time)
        return generate_latest()

# Global instance
metrics_collector = SimpleMetricsCollector()

# ========================================
# ENDPOINT
# ========================================

def get_metrics_response() -> Response:
    """Return metrics"""
    try:
        return Response(
            content=metrics_collector.get_metrics(),
            media_type=CONTENT_TYPE_LATEST,
            headers={CACHE_CONTROL_HEADER: NO_CACHE_VALUE}
        )
    except Exception as e:
        logger.error(action=LogActions.ERROR, message=f"Metrics error: {e}")
        return Response(content=ERROR_CONTENT, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)