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
import sys
import os
import logging
import json
import time
import uuid
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

# Load environment variables from services/.env
try:
    from dotenv import load_dotenv

    # Find the services root directory (go up from order-service/src to services/)
    services_root = Path(__file__).parent.parent.parent
    env_file = services_root / ".env"

    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ Environment loaded from: {env_file}")
    else:
        print(f"⚠️ Environment file not found at: {env_file}")
        print("Continuing with system environment variables...")

except ImportError:
    print("⚠️ python-dotenv not installed. Using system environment variables only.")

# Configure logging for CloudWatch
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Detect if running in Lambda
IS_LAMBDA = "AWS_LAMBDA_FUNCTION_NAME" in os.environ

# Initialize STS client for AWS role assumption
try:
    from common.aws.sts_client import STSClient
    sts_client = STSClient()
    logger.info("✅ STS client initialized for role assumption")
except ImportError:
    sts_client = None
    logger.info("⚠️ STS client not available, using local credentials")

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
    """Universal logging middleware that works in Lambda and K8s"""
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

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    # TODO: Implement global exception handler tomorrow
    # from exceptions.secure_exceptions import secure_general_exception_handler
    # return await secure_general_exception_handler(request, exc)
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Import and include API routers
try:
    from controllers.health import router as health_router
    app.include_router(health_router, tags=["health"])
    logger.info("✅ Health routes loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ Health routes not available: {e}")

try:
    from controllers.create_order import router as create_order_router
    from controllers.get_order import router as get_order_router
    from controllers.list_orders import router as list_orders_router

    # Include all order controllers
    app.include_router(create_order_router, prefix="/orders", tags=["orders"])
    app.include_router(get_order_router, prefix="/orders", tags=["orders"])
    app.include_router(list_orders_router, prefix="/orders", tags=["orders"])

    logger.info("✅ Order controllers loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ Order controllers not available: {e}")

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
            "environment": os.getenv("ENVIRONMENT", "development"),
            "lambda": IS_LAMBDA
        }
    }

# Enhanced startup event
@app.on_event("startup")
async def startup_event():
    """Startup event handler - API service initialization"""
    logger.info("🚀 Order Service starting up...")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"Lambda Environment: {IS_LAMBDA}")

    # Log environment configuration
    logger.info("📊 API Service Configuration:")
    logger.info(f"  Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"  Services Root: {Path(__file__).parent.parent.parent}")
    logger.info(f"  Service: order-processing")
    logger.info(f"  Database: Accessed via DAO layer in common package")

    # Check required environment variables
    required_env_vars = {
        "USERS_TABLE": os.getenv("USERS_TABLE"),
        "ORDERS_TABLE": os.getenv("ORDERS_TABLE"),
        "INVENTORY_TABLE": os.getenv("INVENTORY_TABLE")
    }

    logger.info("🔧 Environment Variables:")
    for var_name, var_value in required_env_vars.items():
        if var_value:
            logger.info(f"  {var_name}: ✅ Configured")
        else:
            logger.warning(f"  {var_name}: ❌ Missing")

    # Log available endpoints
    logger.info("🎯 Available endpoints:")
    logger.info("  GET  /health - Basic health check (liveness probe)")
    logger.info("  GET  /health/ready - Readiness probe")
    logger.info("  GET  /health/db - Database health check")
    logger.info("  POST /orders - Create new order")
    logger.info("  GET  /orders/{order_id} - Get order by ID")
    logger.info("  GET  /orders - List user orders")
    logger.info("  GET  /docs - API documentation")

    logger.info("✅ Order Service startup complete!")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("👋 Order Service shutting down...")

# For local development
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    logger.info(f"Starting server on {host}:{port}")
    logger.info("🔧 Development Mode:")
    logger.info("  - Auto-reload enabled")
    logger.info("  - CORS configured for development")
    logger.info("  - Detailed logging enabled")
    logger.info("  - CloudWatch logging middleware active")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,  # Enable reload for development
        log_level="info"
    )