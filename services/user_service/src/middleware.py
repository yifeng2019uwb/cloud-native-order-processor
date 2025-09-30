"""
User Service Middleware - Metrics Collection
"""
import time
from fastapi import Request, Response
from common.shared.logging import BaseLogger, Loggers, LogActions
from metrics import metrics_collector

logger = BaseLogger(Loggers.USER)

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
        metrics_collector.record_user_request(endpoint, status, duration)

        # Record specific operation metrics based on endpoint
        if "/auth/login" in endpoint:
            metrics_collector.record_auth_operation("login", status, duration)
        elif "/auth/register" in endpoint:
            metrics_collector.record_auth_operation("register", status, duration)
        elif "/auth/logout" in endpoint:
            metrics_collector.record_auth_operation("logout", status, duration)
        elif "/auth/profile" in endpoint:
            metrics_collector.record_auth_operation("profile", status, duration)
        elif "/balance" in endpoint:
            operation = "get_balance" if "GET" in request.method else "balance_operation"
            metrics_collector.record_balance_operation(operation, status, duration)
        elif "/deposit" in endpoint:
            metrics_collector.record_balance_operation("deposit", status, duration)
        elif "/withdraw" in endpoint:
            metrics_collector.record_balance_operation("withdraw", status, duration)
        elif "/transactions" in endpoint:
            metrics_collector.record_balance_operation("transactions", status, duration)

        return response

    except Exception as e:
        # Calculate duration even for exceptions
        duration = time.time() - start_time

        # Record error metrics
        metrics_collector.record_user_request(endpoint, "error", duration)

        # Record specific operation metrics for errors
        if "/auth/login" in endpoint:
            metrics_collector.record_auth_operation("login", "error", duration)
        elif "/auth/register" in endpoint:
            metrics_collector.record_auth_operation("register", "error", duration)
        elif "/auth/logout" in endpoint:
            metrics_collector.record_auth_operation("logout", "error", duration)
        elif "/auth/profile" in endpoint:
            metrics_collector.record_auth_operation("profile", "error", duration)
        elif "/balance" in endpoint:
            operation = "get_balance" if "GET" in request.method else "balance_operation"
            metrics_collector.record_balance_operation(operation, "error", duration)
        elif "/deposit" in endpoint:
            metrics_collector.record_balance_operation("deposit", "error", duration)
        elif "/withdraw" in endpoint:
            metrics_collector.record_balance_operation("withdraw", "error", duration)
        elif "/transactions" in endpoint:
            metrics_collector.record_balance_operation("transactions", "error", duration)

        # Re-raise the exception
        raise
