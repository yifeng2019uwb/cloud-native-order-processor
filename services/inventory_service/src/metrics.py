"""
Prometheus metrics for Inventory Service
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request
import time

# Request metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Business metrics
ASSETS_RETRIEVED = Counter(
    'assets_retrieved_total',
    'Total number of assets retrieved',
    ['category', 'active_only']
)

ASSET_DETAILS_VIEWED = Counter(
    'asset_details_viewed_total',
    'Total number of asset detail views',
    ['asset_id']
)

# System metrics
ACTIVE_CONNECTIONS = Gauge(
    'active_database_connections',
    'Number of active database connections'
)

DATABASE_OPERATION_DURATION = Histogram(
    'database_operation_duration_seconds',
    'Database operation duration in seconds',
    ['operation', 'table']
)

# Custom metrics for business insights
TOTAL_ASSETS = Gauge(
    'total_assets',
    'Total number of assets in inventory'
)

ACTIVE_ASSETS = Gauge(
    'active_assets',
    'Number of active assets in inventory'
)

def get_metrics():
    """Return Prometheus metrics"""
    return generate_latest()

async def metrics_middleware(request: Request, call_next):
    """Middleware to collect request metrics"""
    start_time = time.time()

    # Process the request
    response = await call_next(request)

    # Calculate duration
    duration = time.time() - start_time

    # Record metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()

    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)

    return response

def record_asset_retrieval(category: str = None, active_only: bool = False):
    """Record asset retrieval metrics"""
    ASSETS_RETRIEVED.labels(
        category=category or 'all',
        active_only=str(active_only)
    ).inc()

def record_asset_detail_view(asset_id: str):
    """Record asset detail view metrics"""
    ASSET_DETAILS_VIEWED.labels(asset_id=asset_id).inc()

def update_asset_counts(total: int, active: int):
    """Update asset count metrics"""
    TOTAL_ASSETS.set(total)
    ACTIVE_ASSETS.set(active)

def record_database_operation(operation: str, table: str, duration: float):
    """Record database operation metrics"""
    DATABASE_OPERATION_DURATION.labels(
        operation=operation,
        table=table
    ).observe(duration)