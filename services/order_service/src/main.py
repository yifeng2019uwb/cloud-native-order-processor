"""
Order Service - FastAPI Application Entry Point
"""
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from common.shared.logging import BaseLogger, Loggers, LogActions
from controllers import (
    create_order_router,
    get_order_router,
    list_orders_router,
    portfolio_router,
    asset_balance_router,
    asset_transaction_router,
    health_router
)

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

# Include API routers
app.include_router(health_router, tags=["health"])
app.include_router(create_order_router, prefix="/orders", tags=["orders"])
app.include_router(get_order_router, prefix="/orders", tags=["orders"])
app.include_router(list_orders_router, prefix="/orders", tags=["orders"])
app.include_router(portfolio_router, tags=["portfolio"])
app.include_router(asset_balance_router, tags=["asset-balances"])
app.include_router(asset_transaction_router, tags=["asset-transactions"])

@app.exception_handler(Exception)
def general_exception_handler(request, exc):
    logger.error(action=LogActions.ERROR, message=f"Unhandled error: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

# Root endpoint
@app.get("/")
def root():
    """Root endpoint with service information"""
    return {
        "service": "Order Service",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "orders": "/orders",
            "order_detail": "/orders/{order_id}",
            "portfolio": "/portfolio/{username}",
            "asset_balances": "/assets/balances",
            "asset_transactions": "/assets/{asset_id}/transactions"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)