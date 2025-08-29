"""
FastAPI Application Entry Point - Order Service
Path: services/order-service/src/main.py

This is the API layer entry point. It handles:
- API routing and middleware
- Exception handling
- Service configuration
- Environment variables loaded from services/.env
- CloudWatch logging for Lambda deployment
"""
import os
from datetime import datetime
from pathlib import Path
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from common.shared.logging import BaseLogger, Loggers, LogActions
from common.aws.sts_client import STSClient
from order_exceptions import CNOPOrderValidationException
from controllers import (
    create_order_router,
    get_order_router,
    list_orders_router,
    portfolio_router,
    asset_balance_router,
    asset_transaction_router,
    health_router
)

# Initialize our standardized logger
logger = BaseLogger(Loggers.ORDER)

# Load environment variables from services/.env
services_root = Path(__file__).parent.parent.parent
env_file = services_root / ".env"

if env_file.exists():
    load_dotenv(env_file)
    logger.info(action=LogActions.SERVICE_START, message=f"Environment loaded from: {env_file}")
else:
    logger.warning(action=LogActions.ERROR, message=f"Environment file not found at: {env_file}")
    logger.info(action=LogActions.SERVICE_START, message="Continuing with system environment variables...")

# Initialize STS client for AWS role assumption
sts_client = STSClient()
logger.info(action=LogActions.SERVICE_START, message="STS client initialized for role assumption")

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

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Logging middleware for K8s deployment"""
    # TODO: Implement logging middleware
    response = await call_next(request)
    return response

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    # TODO: Implement validation error handler tomorrow
    # from exceptions.secure_exceptions import secure_validation_exception_handler
    # return await secure_validation_exception_handler(request, exc)
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": exc.errors()}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    # TODO: Implement HTTP exception handler tomorrow
    # from exceptions.secure_exceptions import secure_general_exception_handler
    # return await secure_general_exception_handler(request, exc)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(CNOPOrderValidationException)
async def order_validation_exception_handler(request: Request, exc: CNOPOrderValidationException):
    """Handle order validation exceptions"""
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    # TODO: Implement global exception handler tomorrow
    # from exceptions.secure_exceptions import secure_general_exception_handler
    # return await secure_general_exception_handler(request, exc)
    logger.error(action=LogActions.ERROR, message=f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Include API routers
app.include_router(health_router, tags=["health"])
logger.info(action=LogActions.SERVICE_START, message="Health routes loaded successfully")

# Include order controllers
app.include_router(create_order_router, prefix="/orders", tags=["orders"])
logger.info(action=LogActions.SERVICE_START, message="Create order routes loaded successfully")

app.include_router(get_order_router, prefix="/orders", tags=["orders"])
logger.info(action=LogActions.SERVICE_START, message="Get order routes loaded successfully")

app.include_router(list_orders_router, prefix="/orders", tags=["orders"])
logger.info(action=LogActions.SERVICE_START, message="List orders routes loaded successfully")

# Include portfolio and asset management controllers
app.include_router(portfolio_router, tags=["portfolio"])
logger.info(action=LogActions.SERVICE_START, message="Portfolio routes loaded successfully")

app.include_router(asset_balance_router, tags=["asset-balances"])
logger.info(action=LogActions.SERVICE_START, message="Asset balance routes loaded successfully")

app.include_router(asset_transaction_router, tags=["asset-transactions"])
logger.info(action=LogActions.SERVICE_START, message="Asset transaction routes loaded successfully")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Order Service",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "orders": "/orders"
        },
        "environment": {
            "service": "order-service",
            "environment": os.getenv("ENVIRONMENT", "development")
        }
    }

# Enhanced startup event
@app.on_event("startup")
async def startup_event():
    """Startup event handler - API service initialization"""
    logger.info(action=LogActions.SERVICE_START, message="Order Service starting up...")
    logger.info(action=LogActions.SERVICE_START, message=f"Environment: {os.getenv('ENVIRONMENT', 'development')}")

    # Log environment configuration
    logger.info(action=LogActions.SERVICE_START, message="API Service Configuration:")
    logger.info(action=LogActions.SERVICE_START, message=f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(action=LogActions.SERVICE_START, message=f"Services Root: {Path(__file__).parent.parent.parent}")
    logger.info(action=LogActions.SERVICE_START, message="Service: order-processing")
    logger.info(action=LogActions.SERVICE_START, message="Database: Accessed via DAO layer in common package")

    # Check required environment variables
    required_env_vars = {
        "USERS_TABLE": os.getenv("USERS_TABLE"),
        "ORDERS_TABLE": os.getenv("ORDERS_TABLE"),
        "INVENTORY_TABLE": os.getenv("INVENTORY_TABLE")
    }

    logger.info(action=LogActions.SERVICE_START, message="Environment Variables:")
    for var_name, var_value in required_env_vars.items():
        if var_value:
            logger.info(action=LogActions.SERVICE_START, message=f"{var_name}: Configured")
        else:
            logger.warning(action=LogActions.ERROR, message=f"{var_name}: Missing")

    # Log available endpoints
    logger.info(action=LogActions.SERVICE_START, message="Available endpoints:")
    logger.info(action=LogActions.SERVICE_START, message="GET  /health - Basic health check (liveness probe)")
    logger.info(action=LogActions.SERVICE_START, message="GET  /health/ready - Readiness probe")
    logger.info(action=LogActions.SERVICE_START, message="GET  /health/db - Database health check")
    logger.info(action=LogActions.SERVICE_START, message="POST /orders - Create new order")
    logger.info(action=LogActions.SERVICE_START, message="GET  /orders/{order_id} - Get order by ID")
    logger.info(action=LogActions.SERVICE_START, message="GET  /orders - List user orders")
    logger.info(action=LogActions.SERVICE_START, message="GET  /portfolio/{username} - Get user portfolio")
    logger.info(action=LogActions.SERVICE_START, message="GET  /assets/balances - Get all asset balances")
    logger.info(action=LogActions.SERVICE_START, message="GET  /assets/{asset_id}/balance - Get specific asset balance")
    logger.info(action=LogActions.SERVICE_START, message="GET  /assets/{asset_id}/transactions - Get asset transaction history")

    logger.info(action=LogActions.SERVICE_START, message="GET  /docs - API documentation")

    logger.info(action=LogActions.SERVICE_START, message="Order Service startup complete!")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info(action=LogActions.SERVICE_START, message="👋 Order Service shutting down...")

# For local development
if __name__ == "__main__":

    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    logger.info(action=LogActions.SERVICE_START, message=f"Starting server on {host}:{port}")
    logger.info(action=LogActions.SERVICE_START, message="🔧 Development Mode:")
    logger.info(action=LogActions.SERVICE_START, message="  - Auto-reload enabled")
    logger.info(action=LogActions.SERVICE_START, message="  - CORS configured for development")
    logger.info(action=LogActions.SERVICE_START, message="  - Detailed logging enabled")
    logger.info(action=LogActions.SERVICE_START, message="  - CloudWatch logging middleware active")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,  # Enable reload for development
        log_level="info"
    )