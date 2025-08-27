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
import logging
import uvicorn
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from order_exceptions import CNOPOrderValidationException
from common.aws.sts_client import STSClient

# Controller imports will be moved to after logger setup to avoid JWT import issues

# Load environment variables from services/.env
try:
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

# Import controllers from the controllers package
from controllers import (
    create_order_router,
    get_order_router,
    list_orders_router,
    portfolio_router,
    asset_balance_router,
    asset_transaction_router,
    health_router
)

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
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Import and include API routers
if health_router:
    try:
        app.include_router(health_router, tags=["health"])
        logger.info("✅ Health routes loaded successfully")
    except Exception as e:
        logger.warning(f"⚠️ Health routes not available: {e}")
else:
    logger.warning("⚠️ Health controller not available - skipping health routes")

# Include order controllers if available
if create_order_router:
    try:
        app.include_router(create_order_router, prefix="/orders", tags=["orders"])
        logger.info("✅ Create order routes loaded successfully")
    except Exception as e:
        logger.warning(f"⚠️ Create order routes not available: {e}")
else:
    logger.warning("⚠️ Create order controller not available - skipping routes")

if get_order_router:
    try:
        app.include_router(get_order_router, prefix="/orders", tags=["orders"])
        logger.info("✅ Get order routes loaded successfully")
    except Exception as e:
        logger.warning(f"⚠️ Get order routes not available: {e}")
else:
    logger.warning("⚠️ Get order controller not available - skipping routes")

if list_orders_router:
    try:
        app.include_router(list_orders_router, prefix="/orders", tags=["orders"])
        logger.info("✅ List orders routes loaded successfully")
    except Exception as e:
        logger.warning(f"⚠️ List orders routes not available: {e}")
else:
    logger.warning("⚠️ List orders controller not available - skipping routes")

# Include portfolio and asset management controllers if available
if portfolio_router:
    try:
        app.include_router(portfolio_router, tags=["portfolio"])
        logger.info("✅ Portfolio routes loaded successfully")
    except Exception as e:
        logger.warning(f"⚠️ Portfolio routes not available: {e}")
else:
    logger.warning("⚠️ Portfolio controller not available - skipping routes")

if asset_balance_router:
    try:
        app.include_router(asset_balance_router, tags=["asset-balances"])
        logger.info("✅ Asset balance routes loaded successfully")
    except Exception as e:
        logger.warning(f"⚠️ Asset balance routes not available: {e}")
else:
    logger.warning("⚠️ Asset balance controller not available - skipping routes")

if asset_transaction_router:
    try:
        app.include_router(asset_transaction_router, tags=["asset-transactions"])
        logger.info("✅ Asset transaction routes loaded successfully")
    except Exception as e:
        logger.warning(f"⚠️ Asset transaction routes not available: {e}")
else:
    logger.warning("⚠️ Asset transaction controller not available - skipping routes")

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
    logger.info("🚀 Order Service starting up...")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")

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
    logger.info("  GET  /portfolio/{username} - Get user portfolio")
    logger.info("  GET  /assets/balances - Get all asset balances")
    logger.info("  GET  /assets/{asset_id}/balance - Get specific asset balance")
    logger.info("  GET  /assets/{asset_id}/transactions - Get asset transaction history")

    logger.info("  GET  /docs - API documentation")

    logger.info("✅ Order Service startup complete!")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("👋 Order Service shutting down...")

# For local development
if __name__ == "__main__":

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