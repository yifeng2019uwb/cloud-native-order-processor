"""
Inventory Service Middleware - Metrics Collection
"""
import time
from fastapi import Request, Response
from common.shared.logging import BaseLogger, Loggers, LogActions
from metrics import metrics_collector

logger = BaseLogger(Loggers.INVENTORY)

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
        metrics_collector.record_inventory_request(endpoint, status, duration)

        # Record specific operation metrics based on endpoint
        if "/inventory/assets" in endpoint and request.method == "GET":
            # Check if it's a specific asset or list
            if "/inventory/assets/" in endpoint and endpoint.count("/") > 3:
                metrics_collector.record_asset_operation("get_asset_detail", status, duration)
            else:
                metrics_collector.record_asset_operation("list_assets", status, duration)
        elif "/inventory/assets" in endpoint and request.method == "POST":
            metrics_collector.record_asset_operation("create_asset", status, duration)
        elif "/inventory/assets" in endpoint and request.method == "PUT":
            metrics_collector.record_asset_operation("update_asset", status, duration)
        elif "/inventory/assets" in endpoint and request.method == "DELETE":
            metrics_collector.record_asset_operation("delete_asset", status, duration)

        # Record API call metrics for external calls
        if "coingecko" in str(request.url) or "api" in endpoint:
            metrics_collector.record_api_call("coingecko", status, duration)

        return response

    except Exception as e:
        # Calculate duration even for exceptions
        duration = time.time() - start_time

        # Record error metrics
        metrics_collector.record_inventory_request(endpoint, "error", duration)

        # Record specific operation metrics for errors
        if "/inventory/assets" in endpoint and request.method == "GET":
            if "/inventory/assets/" in endpoint and endpoint.count("/") > 3:
                metrics_collector.record_asset_operation("get_asset_detail", "error", duration)
            else:
                metrics_collector.record_asset_operation("list_assets", "error", duration)
        elif "/inventory/assets" in endpoint and request.method == "POST":
            metrics_collector.record_asset_operation("create_asset", "error", duration)
        elif "/inventory/assets" in endpoint and request.method == "PUT":
            metrics_collector.record_asset_operation("update_asset", "error", duration)
        elif "/inventory/assets" in endpoint and request.method == "DELETE":
            metrics_collector.record_asset_operation("delete_asset", "error", duration)

        # Record API call metrics for errors
        if "coingecko" in str(request.url) or "api" in endpoint:
            metrics_collector.record_api_call("coingecko", "error", duration)

        # Re-raise the exception
        raise
