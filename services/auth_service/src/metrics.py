"""
Auth Service Metrics - Simplified for Personal Project
"""

import time
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
from common.shared.logging import BaseLogger, Loggers, LogActions
from api_info_enum import ServiceMetadata

logger = BaseLogger(Loggers.AUTH)

# ========================================
# SIMPLE METRICS
# ========================================

# Service info
service_info = Info('auth_service_info', 'Auth service information')
service_info.info({'version': ServiceMetadata.VERSION.value, 'service': ServiceMetadata.NAME.value})

# Core counters
auth_requests_total = Counter('auth_requests_total', 'Total auth requests', ['status'])
jwt_validations_total = Counter('jwt_validations_total', 'Total JWT validations', ['result'])

# Simple histogram
request_duration = Histogram('auth_request_duration_seconds', 'Request duration', ['status'])

# Uptime
service_uptime = Gauge('auth_service_uptime_seconds', 'Service uptime')
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
            headers={"Cache-Control": "no-cache"}
        )
    except Exception as e:
        logger.error(action=LogActions.ERROR, message=f"Metrics error: {e}")
        return Response(content="# Error\n", status_code=HTTPStatus.INTERNAL_SERVER_ERROR)