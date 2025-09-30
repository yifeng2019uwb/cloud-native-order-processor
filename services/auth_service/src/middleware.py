"""
Auth Service Middleware - Metrics Collection
"""
import time
from fastapi import Request, Response
from common.shared.logging import BaseLogger, Loggers, LogActions
from metrics import metrics_collector

logger = BaseLogger(Loggers.AUTH)

async def metrics_middleware(request: Request, call_next):
    """Middleware to collect request metrics automatically"""
    start_time = time.time()

    # Extract endpoint path for metrics
    endpoint = request.url.path

    try:
        # Process the request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Determine status based on response
        status = "success" if 200 <= response.status_code < 400 else "error"

        # Record metrics
        metrics_collector.record_request(status, duration)

        # Record specific operation metrics based on endpoint
        if "/internal/auth/validate" in endpoint:
            metrics_collector.record_jwt_validation(status, duration)

        return response

    except Exception as e:
        # Calculate duration even for exceptions
        duration = time.time() - start_time

        # Record error metrics
        metrics_collector.record_request("error", duration)

        # Record specific operation metrics for errors
        if "/internal/auth/validate" in endpoint:
            metrics_collector.record_jwt_validation("error", duration)

        # Re-raise the exception
        raise
