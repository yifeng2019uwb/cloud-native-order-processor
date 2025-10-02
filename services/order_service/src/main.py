"""
Order Service - FastAPI Application Entry Point
"""
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from common.shared.logging import BaseLogger, Loggers, LogActions
from common.exceptions import (
    CNOPAssetNotFoundException,
    CNOPUserNotFoundException,
    CNOPOrderNotFoundException,
    CNOPInternalServerException
)
from order_exceptions import (
    CNOPOrderAlreadyExistsException,
    CNOPOrderServerException,
    CNOPOrderValidationException
)
from controllers import (
    create_order_router,
    get_order_router,
    list_orders_router,
    asset_transaction_router,
    health_router
)
from metrics import get_metrics_response
from constants import METRICS_ENDPOINT, SERVICE_NAME, SERVICE_VERSION
from middleware import metrics_middleware

# Initialize logger
logger = BaseLogger(Loggers.ORDER)

# Create FastAPI app
app = FastAPI(
    title="Order Service",
    description="A cloud-native order processing service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add metrics middleware
app.middleware("http")(metrics_middleware)

# Include API routers
app.include_router(health_router, tags=["health"])
app.include_router(create_order_router, prefix="/orders", tags=["orders"])
app.include_router(get_order_router, prefix="/orders", tags=["orders"])
app.include_router(list_orders_router, prefix="/orders", tags=["orders"])
app.include_router(asset_transaction_router, tags=["asset-transactions"])

# Add internal metrics endpoint
@app.get(METRICS_ENDPOINT)
def internal_metrics():
    """Internal Prometheus metrics endpoint for monitoring"""
    return get_metrics_response()

# Custom exception handlers
@app.exception_handler(CNOPOrderValidationException)
def order_validation_exception_handler(request, exc):
    logger.warning(action=LogActions.VALIDATION_ERROR, message=f"Order validation error: {exc}")
    return JSONResponse(status_code=422, content={"detail": str(exc)})

@app.exception_handler(CNOPOrderAlreadyExistsException)
def order_already_exists_exception_handler(request, exc):
    logger.warning(action=LogActions.VALIDATION_ERROR, message=f"Order already exists: {exc}")
    return JSONResponse(status_code=409, content={"detail": str(exc)})

@app.exception_handler(CNOPUserNotFoundException)
def user_not_found_exception_handler(request, exc):
    logger.warning(action=LogActions.VALIDATION_ERROR, message=f"User not found: {exc}")
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@app.exception_handler(CNOPAssetNotFoundException)
def asset_not_found_exception_handler(request, exc):
    logger.warning(action=LogActions.VALIDATION_ERROR, message=f"Asset not found: {exc}")
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@app.exception_handler(CNOPOrderNotFoundException)
def order_not_found_exception_handler(request, exc):
    logger.warning(action=LogActions.VALIDATION_ERROR, message=f"Order not found: {exc}")
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@app.exception_handler(CNOPOrderServerException)
def order_server_exception_handler(request, exc):
    logger.error(action=LogActions.ERROR, message=f"Order server error: {exc}")
    return JSONResponse(status_code=500, content={"detail": str(exc)})

@app.exception_handler(CNOPInternalServerException)
def internal_server_exception_handler(request, exc):
    logger.error(action=LogActions.ERROR, message=f"Internal server error: {exc}")
    return JSONResponse(status_code=500, content={"detail": str(exc)})

@app.exception_handler(Exception)
def general_exception_handler(request, exc):
    logger.error(action=LogActions.ERROR, message=f"Unhandled error: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

# Root endpoint
@app.get("/")
def root():
    """Root endpoint with service information"""
    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "status": "running",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "orders": "/orders",
            "order_detail": "/orders/{order_id}",
            "asset_transactions": "/assets/{asset_id}/transactions",
            "metrics": METRICS_ENDPOINT
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)