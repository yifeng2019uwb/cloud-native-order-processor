"""
User Service Metrics - Simplified for Personal Project
"""

import time
from enum import Enum
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
from common.shared.logging import BaseLogger, LogAction, LoggerName
from common.shared.constants.api_constants import HTTPStatus
from api_info_enum import ServiceMetadata


class MetricsMetadata(str, Enum):
    """Prometheus metrics metadata - for type safety and validation"""
    SERVICE_INFO = "user_service_info"
    SERVICE_DESCRIPTION = "User service information"
    USER_REQUESTS_TOTAL = "user_requests_total"
    AUTH_OPERATIONS_TOTAL = "auth_operations_total"
    BALANCE_OPERATIONS_TOTAL = "balance_operations_total"
    REQUEST_DURATION = "user_request_duration_seconds"
    AUTH_DURATION = "auth_operation_duration_seconds"
    BALANCE_DURATION = "balance_operation_duration_seconds"
    SERVICE_UPTIME = "user_service_uptime_seconds"


# =============================================================================
# METRICS MESSAGES (Local constants for descriptions)
# =============================================================================
MSG_TOTAL_USER_REQUESTS = "Total user requests"
MSG_TOTAL_AUTH_OPERATIONS = "Total auth operations"
MSG_TOTAL_BALANCE_OPERATIONS = "Total balance operations"
MSG_REQUEST_DURATION = "Request duration"
MSG_AUTH_OPERATION_DURATION = "Auth operation duration"
MSG_BALANCE_OPERATION_DURATION = "Balance operation duration"
MSG_SERVICE_UPTIME = "Service uptime"

# =============================================================================
# METRICS LABELS (Local constants for label names)
# =============================================================================
LABEL_STATUS = "status"
LABEL_ENDPOINT = "endpoint"
LABEL_OPERATION = "operation"
LABEL_RESULT = "result"

# =============================================================================
# METRICS INFO KEYS (Local constants for info dictionary keys)
# =============================================================================
INFO_KEY_VERSION = "version"
INFO_KEY_SERVICE = "service"

# =============================================================================
# RESPONSE CONSTANTS (Local constants for response handling)
# =============================================================================
CACHE_CONTROL_HEADER = "Cache-Control"
NO_CACHE_VALUE = "no-cache"
ERROR_CONTENT = "# Error\n"

logger = BaseLogger(LoggerName.USER)

# ========================================
# SIMPLE METRICS
# ========================================

# Service info
service_info = Info(MetricsMetadata.SERVICE_INFO.value, MetricsMetadata.SERVICE_DESCRIPTION.value)
service_info.info({INFO_KEY_VERSION: ServiceMetadata.VERSION.value, INFO_KEY_SERVICE: ServiceMetadata.NAME.value})

# Core counters
user_requests_total = Counter(MetricsMetadata.USER_REQUESTS_TOTAL.value, MSG_TOTAL_USER_REQUESTS, [LABEL_STATUS, LABEL_ENDPOINT])
auth_operations_total = Counter(MetricsMetadata.AUTH_OPERATIONS_TOTAL.value, MSG_TOTAL_AUTH_OPERATIONS, [LABEL_OPERATION, LABEL_RESULT])
balance_operations_total = Counter(MetricsMetadata.BALANCE_OPERATIONS_TOTAL.value, MSG_TOTAL_BALANCE_OPERATIONS, [LABEL_OPERATION, LABEL_RESULT])

# Simple histograms
request_duration = Histogram(MetricsMetadata.REQUEST_DURATION.value, MSG_REQUEST_DURATION, [LABEL_STATUS, LABEL_ENDPOINT])
auth_duration = Histogram(MetricsMetadata.AUTH_DURATION.value, MSG_AUTH_OPERATION_DURATION, [LABEL_OPERATION])
balance_duration = Histogram(MetricsMetadata.BALANCE_DURATION.value, MSG_BALANCE_OPERATION_DURATION, [LABEL_OPERATION])

# Uptime
service_uptime = Gauge(MetricsMetadata.SERVICE_UPTIME.value, MSG_SERVICE_UPTIME)
_start_time = time.time()

# ========================================
# SIMPLE COLLECTOR
# ========================================

class SimpleMetricsCollector:
    """Simple metrics collector"""

    def record_user_request(self, endpoint: str, status: str, duration: float = None):
        """Record user request"""
        user_requests_total.labels(**{LABEL_STATUS: status, LABEL_ENDPOINT: endpoint}).inc()
        if duration:
            request_duration.labels(**{LABEL_STATUS: status, LABEL_ENDPOINT: endpoint}).observe(duration)

    def record_auth_operation(self, operation: str, result: str, duration: float = None):
        """Record auth operation"""
        auth_operations_total.labels(**{LABEL_OPERATION: operation, LABEL_RESULT: result}).inc()
        if duration:
            auth_duration.labels(**{LABEL_OPERATION: operation}).observe(duration)

    def record_balance_operation(self, operation: str, result: str, duration: float = None):
        """Record balance operation"""
        balance_operations_total.labels(**{LABEL_OPERATION: operation, LABEL_RESULT: result}).inc()
        if duration:
            balance_duration.labels(**{LABEL_OPERATION: operation}).observe(duration)

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
        logger.error(action=LogAction.ERROR, message=f"Metrics error: {e}")
        return Response(content=ERROR_CONTENT, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
