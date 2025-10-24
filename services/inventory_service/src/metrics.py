"""
Inventory Service Metrics - Simplified for Personal Project
"""
import time
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
from common.shared.logging import BaseLogger, LoggerName, LogAction
from common.shared.constants.api_constants import HTTPStatus
from api_info_enum import ServiceMetadata

logger = BaseLogger(LoggerName.INVENTORY)

# =============================================================================
# METRICS CONSTANTS (Local constants for this service)
# =============================================================================

# Service info constants
SERVICE_INFO_NAME = "inventory_service_info"
SERVICE_INFO_DESCRIPTION = "Inventory service information"

# Metrics names
INVENTORY_REQUESTS_TOTAL = "inventory_requests_total"
ASSET_OPERATIONS_TOTAL = "asset_operations_total"
API_CALLS_TOTAL = "api_calls_total"
REQUEST_DURATION = "inventory_request_duration_seconds"
ASSET_DURATION = "asset_operation_duration_seconds"
API_DURATION = "api_call_duration_seconds"
SERVICE_UPTIME = "inventory_service_uptime_seconds"

# Metrics descriptions
MSG_TOTAL_INVENTORY_REQUESTS = "Total inventory requests"
MSG_TOTAL_ASSET_OPERATIONS = "Total asset operations"
MSG_TOTAL_API_CALLS = "Total external API calls"
MSG_REQUEST_DURATION = "Request duration"
MSG_ASSET_OPERATION_DURATION = "Asset operation duration"
MSG_API_CALL_DURATION = "API call duration"
MSG_SERVICE_UPTIME = "Service uptime"

# Metrics labels
LABEL_STATUS = "status"
LABEL_ENDPOINT = "endpoint"
LABEL_OPERATION = "operation"
LABEL_RESULT = "result"
LABEL_API = "api"

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
service_info.info({INFO_KEY_VERSION: ServiceMetadata.VERSION.value, INFO_KEY_SERVICE: ServiceMetadata.NAME.value})

# Core counters
inventory_requests_total = Counter(INVENTORY_REQUESTS_TOTAL, MSG_TOTAL_INVENTORY_REQUESTS, [LABEL_STATUS, LABEL_ENDPOINT])
asset_operations_total = Counter(ASSET_OPERATIONS_TOTAL, MSG_TOTAL_ASSET_OPERATIONS, [LABEL_OPERATION, LABEL_RESULT])
api_calls_total = Counter(API_CALLS_TOTAL, MSG_TOTAL_API_CALLS, [LABEL_API, LABEL_RESULT])

# Simple histograms
request_duration = Histogram(REQUEST_DURATION, MSG_REQUEST_DURATION, [LABEL_STATUS, LABEL_ENDPOINT])
asset_duration = Histogram(ASSET_DURATION, MSG_ASSET_OPERATION_DURATION, [LABEL_OPERATION])
api_duration = Histogram(API_DURATION, MSG_API_CALL_DURATION, [LABEL_API])

# Uptime
service_uptime = Gauge(SERVICE_UPTIME, MSG_SERVICE_UPTIME)
_start_time = time.time()

# ========================================
# SIMPLE COLLECTOR
# ========================================

class SimpleMetricsCollector:
    """Simple metrics collector"""

    def record_inventory_request(self, endpoint: str, status: str, duration: float = None):
        """Record inventory request"""
        inventory_requests_total.labels(**{LABEL_STATUS: status, LABEL_ENDPOINT: endpoint}).inc()
        if duration:
            request_duration.labels(**{LABEL_STATUS: status, LABEL_ENDPOINT: endpoint}).observe(duration)

    def record_asset_operation(self, operation: str, result: str, duration: float = None):
        """Record asset operation"""
        asset_operations_total.labels(**{LABEL_OPERATION: operation, LABEL_RESULT: result}).inc()
        if duration:
            asset_duration.labels(**{LABEL_OPERATION: operation}).observe(duration)

    def record_api_call(self, api: str, result: str, duration: float = None):
        """Record external API call"""
        api_calls_total.labels(**{LABEL_API: api, LABEL_RESULT: result}).inc()
        if duration:
            api_duration.labels(**{LABEL_API: api}).observe(duration)

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

# Legacy functions for backward compatibility
def get_metrics():
    """Legacy function for backward compatibility"""
    return get_metrics_response().body

async def metrics_middleware(request, call_next):
    """Legacy middleware for backward compatibility"""
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    metrics_collector.record_inventory_request(
        endpoint=request.url.path,
        status=str(response.status_code),
        duration=duration
    )

    return response