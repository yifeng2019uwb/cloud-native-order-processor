"""
User Service Metrics - Simplified for Personal Project
"""

import time
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
from common.shared.logging import BaseLogger, Loggers, LogActions
from constants import SERVICE_NAME, SERVICE_VERSION

logger = BaseLogger(Loggers.USER)

# ========================================
# SIMPLE METRICS
# ========================================

# Service info
service_info = Info('user_service_info', 'User service information')
service_info.info({'version': SERVICE_VERSION, 'service': SERVICE_NAME})

# Core counters
user_requests_total = Counter('user_requests_total', 'Total user requests', ['status', 'endpoint'])
auth_operations_total = Counter('auth_operations_total', 'Total auth operations', ['operation', 'result'])
balance_operations_total = Counter('balance_operations_total', 'Total balance operations', ['operation', 'result'])

# Simple histograms
request_duration = Histogram('user_request_duration_seconds', 'Request duration', ['status', 'endpoint'])
auth_duration = Histogram('auth_operation_duration_seconds', 'Auth operation duration', ['operation'])
balance_duration = Histogram('balance_operation_duration_seconds', 'Balance operation duration', ['operation'])

# Uptime
service_uptime = Gauge('user_service_uptime_seconds', 'Service uptime')
_start_time = time.time()

# ========================================
# SIMPLE COLLECTOR
# ========================================

class SimpleMetricsCollector:
    """Simple metrics collector"""

    def record_user_request(self, endpoint: str, status: str, duration: float = None):
        """Record user request"""
        user_requests_total.labels(status=status, endpoint=endpoint).inc()
        if duration:
            request_duration.labels(status=status, endpoint=endpoint).observe(duration)

    def record_auth_operation(self, operation: str, result: str, duration: float = None):
        """Record auth operation"""
        auth_operations_total.labels(operation=operation, result=result).inc()
        if duration:
            auth_duration.labels(operation=operation).observe(duration)

    def record_balance_operation(self, operation: str, result: str, duration: float = None):
        """Record balance operation"""
        balance_operations_total.labels(operation=operation, result=result).inc()
        if duration:
            balance_duration.labels(operation=operation).observe(duration)

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
        return Response(content="# Error\n", status_code=500)
