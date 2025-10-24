"""
Order Service Metrics - Simplified for Personal Project
"""

import time
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
from common.shared.logging import BaseLogger, LoggerName, LogAction
from constants import SERVICE_NAME, SERVICE_VERSION
from common.shared.constants.api_constants import HTTPStatus

logger = BaseLogger(LoggerName.ORDER)

# =============================================================================
# METRICS CONSTANTS (Local constants for this service)
# =============================================================================

# Service info constants
SERVICE_INFO_NAME = "order_service_info"
SERVICE_INFO_DESCRIPTION = "Order service information"

# Metrics names
ORDER_REQUESTS_TOTAL = "order_requests_total"
ORDER_OPERATIONS_TOTAL = "order_operations_total"
PORTFOLIO_OPERATIONS_TOTAL = "portfolio_operations_total"
ASSET_OPERATIONS_TOTAL = "asset_operations_total"
REQUEST_DURATION = "order_request_duration_seconds"
ORDER_DURATION = "order_operation_duration_seconds"
PORTFOLIO_DURATION = "portfolio_operation_duration_seconds"
ASSET_DURATION = "asset_operation_duration_seconds"
SERVICE_UPTIME = "order_service_uptime_seconds"

# Metrics descriptions
MSG_TOTAL_ORDER_REQUESTS = "Total order requests"
MSG_TOTAL_ORDER_OPERATIONS = "Total order operations"
MSG_TOTAL_PORTFOLIO_OPERATIONS = "Total portfolio operations"
MSG_TOTAL_ASSET_OPERATIONS = "Total asset operations"
MSG_REQUEST_DURATION = "Request duration"
MSG_ORDER_OPERATION_DURATION = "Order operation duration"
MSG_PORTFOLIO_OPERATION_DURATION = "Portfolio operation duration"
MSG_ASSET_OPERATION_DURATION = "Asset operation duration"
MSG_SERVICE_UPTIME = "Service uptime"

# Metrics labels
LABEL_STATUS = "status"
LABEL_ENDPOINT = "endpoint"
LABEL_OPERATION = "operation"
LABEL_RESULT = "result"

# Info keys
INFO_KEY_VERSION = "version"
INFO_KEY_SERVICE = "service"

# Response constants
CACHE_CONTROL_HEADER = "Cache-Control"
NO_CACHE_VALUE = "no-cache"
ERROR_CONTENT = "# Error\n"

# ========================================
# SIMPLE METRICS
# ========================================

# Service info
service_info = Info(SERVICE_INFO_NAME, SERVICE_INFO_DESCRIPTION)
service_info.info({INFO_KEY_VERSION: SERVICE_VERSION, INFO_KEY_SERVICE: SERVICE_NAME})

# Core counters
order_requests_total = Counter(ORDER_REQUESTS_TOTAL, MSG_TOTAL_ORDER_REQUESTS, [LABEL_STATUS, LABEL_ENDPOINT])
order_operations_total = Counter(ORDER_OPERATIONS_TOTAL, MSG_TOTAL_ORDER_OPERATIONS, [LABEL_OPERATION, LABEL_RESULT])
portfolio_operations_total = Counter(PORTFOLIO_OPERATIONS_TOTAL, MSG_TOTAL_PORTFOLIO_OPERATIONS, [LABEL_OPERATION, LABEL_RESULT])
asset_operations_total = Counter(ASSET_OPERATIONS_TOTAL, MSG_TOTAL_ASSET_OPERATIONS, [LABEL_OPERATION, LABEL_RESULT])

# Simple histograms
request_duration = Histogram(REQUEST_DURATION, MSG_REQUEST_DURATION, [LABEL_STATUS, LABEL_ENDPOINT])
order_duration = Histogram(ORDER_DURATION, MSG_ORDER_OPERATION_DURATION, [LABEL_OPERATION])
portfolio_duration = Histogram(PORTFOLIO_DURATION, MSG_PORTFOLIO_OPERATION_DURATION, [LABEL_OPERATION])
asset_duration = Histogram(ASSET_DURATION, MSG_ASSET_OPERATION_DURATION, [LABEL_OPERATION])

# Uptime
service_uptime = Gauge(SERVICE_UPTIME, MSG_SERVICE_UPTIME)
_start_time = time.time()

# ========================================
# SIMPLE COLLECTOR
# ========================================

class SimpleMetricsCollector:
    """Simple metrics collector"""

    def record_order_request(self, endpoint: str, status: str, duration: float = None):
        """Record order request"""
        order_requests_total.labels(**{LABEL_STATUS: status, LABEL_ENDPOINT: endpoint}).inc()
        if duration:
            request_duration.labels(**{LABEL_STATUS: status, LABEL_ENDPOINT: endpoint}).observe(duration)

    def record_order_operation(self, operation: str, result: str, duration: float = None):
        """Record order operation"""
        order_operations_total.labels(**{LABEL_OPERATION: operation, LABEL_RESULT: result}).inc()
        if duration:
            order_duration.labels(**{LABEL_OPERATION: operation}).observe(duration)

    def record_portfolio_operation(self, operation: str, result: str, duration: float = None):
        """Record portfolio operation"""
        portfolio_operations_total.labels(**{LABEL_OPERATION: operation, LABEL_RESULT: result}).inc()
        if duration:
            portfolio_duration.labels(**{LABEL_OPERATION: operation}).observe(duration)

    def record_asset_operation(self, operation: str, result: str, duration: float = None):
        """Record asset operation"""
        asset_operations_total.labels(**{LABEL_OPERATION: operation, LABEL_RESULT: result}).inc()
        if duration:
            asset_duration.labels(**{LABEL_OPERATION: operation}).observe(duration)

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
