"""
Order Service Metrics - Simplified for Personal Project
"""

import time
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
from common.shared.logging import BaseLogger, Loggers, LogActions
from constants import SERVICE_NAME, SERVICE_VERSION
from common.shared.constants.http_status import HTTPStatus

logger = BaseLogger(Loggers.ORDER)

# ========================================
# SIMPLE METRICS
# ========================================

# Service info
service_info = Info('order_service_info', 'Order service information')
service_info.info({'version': SERVICE_VERSION, 'service': SERVICE_NAME})

# Core counters
order_requests_total = Counter('order_requests_total', 'Total order requests', ['status', 'endpoint'])
order_operations_total = Counter('order_operations_total', 'Total order operations', ['operation', 'result'])
portfolio_operations_total = Counter('portfolio_operations_total', 'Total portfolio operations', ['operation', 'result'])
asset_operations_total = Counter('asset_operations_total', 'Total asset operations', ['operation', 'result'])

# Simple histograms
request_duration = Histogram('order_request_duration_seconds', 'Request duration', ['status', 'endpoint'])
order_duration = Histogram('order_operation_duration_seconds', 'Order operation duration', ['operation'])
portfolio_duration = Histogram('portfolio_operation_duration_seconds', 'Portfolio operation duration', ['operation'])
asset_duration = Histogram('asset_operation_duration_seconds', 'Asset operation duration', ['operation'])

# Uptime
service_uptime = Gauge('order_service_uptime_seconds', 'Service uptime')
_start_time = time.time()

# ========================================
# SIMPLE COLLECTOR
# ========================================

class SimpleMetricsCollector:
    """Simple metrics collector"""

    def record_order_request(self, endpoint: str, status: str, duration: float = None):
        """Record order request"""
        order_requests_total.labels(status=status, endpoint=endpoint).inc()
        if duration:
            request_duration.labels(status=status, endpoint=endpoint).observe(duration)

    def record_order_operation(self, operation: str, result: str, duration: float = None):
        """Record order operation"""
        order_operations_total.labels(operation=operation, result=result).inc()
        if duration:
            order_duration.labels(operation=operation).observe(duration)

    def record_portfolio_operation(self, operation: str, result: str, duration: float = None):
        """Record portfolio operation"""
        portfolio_operations_total.labels(operation=operation, result=result).inc()
        if duration:
            portfolio_duration.labels(operation=operation).observe(duration)

    def record_asset_operation(self, operation: str, result: str, duration: float = None):
        """Record asset operation"""
        asset_operations_total.labels(operation=operation, result=result).inc()
        if duration:
            asset_duration.labels(operation=operation).observe(duration)

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
