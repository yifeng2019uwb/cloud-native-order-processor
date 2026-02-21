"""
Order Service Middleware - 3 metrics only: requests, errors, latency.
"""
import time
from fastapi import Request
from common.shared.logging import BaseLogger, LoggerName
from api_info_enum import ApiPaths
from metrics import metrics_collector

logger = BaseLogger(LoggerName.ORDER)

_METRICS_SKIP_PATHS = frozenset({
    ApiPaths.METRICS.value,
    ApiPaths.HEALTH.value,
})


def _is_internal_path(path: str) -> bool:
    if not isinstance(path, str):
        return False
    return path in _METRICS_SKIP_PATHS or path.startswith("/health")


async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    endpoint = request.url.path

    try:
        response = await call_next(request)
        duration = time.time() - start_time
        if _is_internal_path(endpoint):
            return response
        metrics_collector.record_request(
            endpoint=endpoint,
            status_code=str(response.status_code),
            duration=duration,
        )
        return response
    except Exception:
        duration = time.time() - start_time
        if _is_internal_path(endpoint):
            raise
        metrics_collector.record_request(endpoint=endpoint, status_code="500", duration=duration)
        raise
