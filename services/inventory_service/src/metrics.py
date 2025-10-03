"""
Inventory Service Metrics - Simplified for Personal Project
"""
import time
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
from common.shared.logging import BaseLogger, Loggers, LogActions
from common.shared.constants.http_status import HTTPStatus
from api_info_enum import ServiceMetadata

logger = BaseLogger(Loggers.INVENTORY)

# ========================================
# SIMPLE METRICS
# ========================================

# Service info
service_info = Info('inventory_service_info', 'Inventory service information')
service_info.info({'version': ServiceMetadata.VERSION.value, 'service': ServiceMetadata.NAME.value})

# Core counters
inventory_requests_total = Counter('inventory_requests_total', 'Total inventory requests', ['status', 'endpoint'])
asset_operations_total = Counter('asset_operations_total', 'Total asset operations', ['operation', 'result'])
api_calls_total = Counter('api_calls_total', 'Total external API calls', ['api', 'result'])

# Simple histograms
request_duration = Histogram('inventory_request_duration_seconds', 'Request duration', ['status', 'endpoint'])
asset_duration = Histogram('asset_operation_duration_seconds', 'Asset operation duration', ['operation'])
api_duration = Histogram('api_call_duration_seconds', 'API call duration', ['api'])

# Uptime
service_uptime = Gauge('inventory_service_uptime_seconds', 'Service uptime')
_start_time = time.time()

# ========================================
# SIMPLE COLLECTOR
# ========================================

class SimpleMetricsCollector:
    """Simple metrics collector"""

    def record_inventory_request(self, endpoint: str, status: str, duration: float = None):
        """Record inventory request"""
        inventory_requests_total.labels(status=status, endpoint=endpoint).inc()
        if duration:
            request_duration.labels(status=status, endpoint=endpoint).observe(duration)

    def record_asset_operation(self, operation: str, result: str, duration: float = None):
        """Record asset operation"""
        asset_operations_total.labels(operation=operation, result=result).inc()
        if duration:
            asset_duration.labels(operation=operation).observe(duration)

    def record_api_call(self, api: str, result: str, duration: float = None):
        """Record external API call"""
        api_calls_total.labels(api=api, result=result).inc()
        if duration:
            api_duration.labels(api=api).observe(duration)

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
            headers={"Cache-Control": "no-cache"}
        )
    except Exception as e:
        logger.error(action=LogActions.ERROR, message=f"Metrics error: {e}")
        return Response(content="# Error\n", status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

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