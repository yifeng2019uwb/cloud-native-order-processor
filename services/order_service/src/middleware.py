"""
Order Service Middleware - Metrics Collection
"""
import time
from fastapi import Request, Response
from common.shared.logging import BaseLogger, LoggerName, LogAction
from metrics import metrics_collector

logger = BaseLogger(LoggerName.ORDER)

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
        metrics_collector.record_order_request(endpoint, status, duration)

        # Record specific operation metrics based on endpoint
        if "/orders" in endpoint and request.method == "POST":
            metrics_collector.record_order_operation("create", status, duration)
        elif "/orders" in endpoint and request.method == "GET":
            metrics_collector.record_order_operation("list", status, duration)
        elif "/orders/" in endpoint and request.method == "GET":
            metrics_collector.record_order_operation("get", status, duration)
        elif "/portfolio" in endpoint:
            metrics_collector.record_portfolio_operation("get_portfolio", status, duration)
        elif "/assets/balances" in endpoint:
            metrics_collector.record_asset_operation("get_balances", status, duration)
        elif "/assets/" in endpoint and "/transactions" in endpoint:
            metrics_collector.record_asset_operation("get_transactions", status, duration)

        return response

    except Exception as e:
        # Calculate duration even for exceptions
        duration = time.time() - start_time

        # Record error metrics
        metrics_collector.record_order_request(endpoint, "error", duration)

        # Record specific operation metrics for errors
        if "/orders" in endpoint and request.method == "POST":
            metrics_collector.record_order_operation("create", "error", duration)
        elif "/orders" in endpoint and request.method == "GET":
            metrics_collector.record_order_operation("list", "error", duration)
        elif "/orders/" in endpoint and request.method == "GET":
            metrics_collector.record_order_operation("get", "error", duration)
        elif "/portfolio" in endpoint:
            metrics_collector.record_portfolio_operation("get_portfolio", "error", duration)
        elif "/assets/balances" in endpoint:
            metrics_collector.record_asset_operation("get_balances", "error", duration)
        elif "/assets/" in endpoint and "/transactions" in endpoint:
            metrics_collector.record_asset_operation("get_transactions", "error", duration)

        # Re-raise the exception
        raise
