"""
FastAPI Application Entry Point - Inventory Service
Path: services/inventory-service/src/main.py

This is the API layer entry point. It handles:
- API routing and middleware
- Exception handling
- Service configuration
- Environment variables loaded from services/.env
- Data initialization on startup
"""
import os
import sys
import uvicorn
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.exceptions import RequestValidationError
from common.aws.sts_client import STSClient
from common.shared.health import HealthChecker
from common.shared.logging import BaseLogger, Loggers, LogActions
from inventory_exceptions.exceptions import (
    CNOPAssetValidationException,
    CNOPInventoryServerException
)
import controllers.assets
import controllers.health
from controllers.assets import router as assets_router
from controllers.health import router as health_router
from data.init_inventory import startup_inventory_initialization
from metrics import metrics_middleware, get_metrics


# Initialize our standardized logger
logger = BaseLogger(Loggers.INVENTORY)

# Load environment variables from services/.env
# Find the services root directory (go up from inventory-service/src to services/)
services_root = Path(__file__).parent.parent.parent
env_file = services_root / ".env"

if env_file.exists():
    load_dotenv(env_file)
    logger.info(action=LogActions.SERVICE_START, message=f"Environment loaded from: {env_file}")
else:
    logger.info(action=LogActions.SERVICE_START, message=f"Environment file not found at: {env_file}, continuing with system environment variables")

# Initialize STS client for AWS role assumption
sts_client = STSClient()
logger.info(action=LogActions.SERVICE_START, message="STS client initialized for role assumption")

# Create FastAPI app
app = FastAPI(
    title="Inventory Service",
    description="A cloud-native inventory management service for crypto assets",
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
logger.info(action=LogActions.SERVICE_START, message="Metrics middleware loaded successfully")

# Define simple exception handlers inline
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Handle validation errors"""
    logger.warning(action=LogActions.VALIDATION_ERROR, message=f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": exc.errors()}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    logger.warning(action=LogActions.ERROR, message=f"HTTP error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(action=LogActions.ERROR, message=f"General error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

logger.info(action=LogActions.SERVICE_START, message="Exception handlers registered successfully")

# Include API routers
app.include_router(assets_router, tags=["inventory"])
logger.info(action=LogActions.SERVICE_START, message="Assets routes loaded successfully")

app.include_router(health_router, tags=["health"])
logger.info(action=LogActions.SERVICE_START, message="Health routes loaded successfully")

# Add metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(
        content=get_metrics(),
        media_type="text/plain"
    )

logger.info(action=LogActions.SERVICE_START, message="Metrics endpoint loaded successfully")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Inventory Service",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "assets": "/inventory/assets",
            "asset_detail": "/inventory/assets/{asset_id}"
        },
        "environment": {
            "service": "inventory-service",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "database_configured": bool(os.getenv('INVENTORY_TABLE'))
        }
    }


# Main health check (API layer only - NO database calls)
@app.get("/health")
def main_health_check():
    """Main application health check - API layer only, no database access"""
    try:
        health_status = {
            "status": "healthy",
            "service": "inventory-service",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "environment": os.getenv("ENVIRONMENT", "development"),
            "checks": {
                "api": "ok",
                "service": "running"
            }
        }

        # Check if required environment variables are set
        required_tables = ["USERS_TABLE", "ORDERS_TABLE", "INVENTORY_TABLE"]
        missing_tables = [table for table in required_tables if not os.getenv(table)]

        if missing_tables:
            health_status["checks"]["configuration"] = f"missing_tables: {missing_tables}"
        else:
            health_status["checks"]["configuration"] = "ok"

        return health_status

    except Exception as e:
        logger.error(action=LogActions.ERROR, message=f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


# Additional health check endpoints using common health checker
try:

    # Create inventory service health checker instance
    health_checker = HealthChecker("inventory-service", "1.0.0")

    @app.get("/health/ready", status_code=200)
    def readiness_check():
        """Readiness check endpoint for Kubernetes readiness probe."""
        return health_checker.readiness_check()

    @app.get("/health/live", status_code=200)
    def liveness_check():
        """Liveness check endpoint for Kubernetes liveness probe."""
        return health_checker.liveness_check()

    @app.get("/health/db", status_code=200)
    def database_health_check():
        """Database health check endpoint."""
        return health_checker.database_health_check()

    logger.info(action=LogActions.SERVICE_START, message="Common health check endpoints loaded successfully")
except ImportError as e:
    logger.warning(action=LogActions.ERROR, message=f"Common health check endpoints not available: {e}")


# Enhanced startup event
@app.on_event("startup")
async def startup_event():
    """Startup event handler - API service initialization"""
    logger.info(action=LogActions.SERVICE_START, message="Inventory Service starting up...")
    logger.info(action=LogActions.SERVICE_START, message=f"Environment: {os.getenv('ENVIRONMENT', 'development')}")

    # Log environment configuration
    logger.info(action=LogActions.SERVICE_START, message="API Service Configuration:")
    logger.info(action=LogActions.SERVICE_START, message=f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(action=LogActions.SERVICE_START, message=f"Services Root: {Path(__file__).parent.parent.parent}")
    logger.info(action=LogActions.SERVICE_START, message=f"Service: inventory-service")
    logger.info(action=LogActions.SERVICE_START, message=f"Database Region: {os.getenv('AWS_REGION', 'Not Set')}")

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

    # Test API router availability
    try:

        logger.info(action=LogActions.SERVICE_START, message="API routes loaded successfully")
    except ImportError as e:
        logger.warning(action=LogActions.ERROR, message=f"Some API routes not available: {e}")

    # Initialize inventory data
    try:

        logger.info(action=LogActions.SERVICE_START, message="Initializing inventory data...")
        init_result = await startup_inventory_initialization()
        logger.info(action=LogActions.SERVICE_START, message=f"Data initialization: {init_result['status']}")
    except ImportError as e:
        logger.warning(action=LogActions.ERROR, message=f"Could not import data initialization: {e}")
    except Exception as e:
        logger.error(action=LogActions.ERROR, message=f"Data initialization failed: {e}")
        # Don't fail startup if data init fails - service can still run

    logger.info(action=LogActions.SERVICE_START, message="Available endpoints:")
    logger.info(action=LogActions.SERVICE_START, message="  GET  / - Service information")
    logger.info(action=LogActions.SERVICE_START, message="  GET  /health - Main health check")
    logger.info(action=LogActions.SERVICE_START, message="  GET  /health/ready - Readiness probe")
    logger.info(action=LogActions.SERVICE_START, message="  GET  /health/live - Liveness probe")
    logger.info(action=LogActions.SERVICE_START, message="  GET  /health/db - Database health")
    logger.info(action=LogActions.SERVICE_START, message="  GET  /inventory/assets - List assets")
    logger.info(action=LogActions.SERVICE_START, message="  GET  /inventory/assets/{id} - Get asset details")
    logger.info(action=LogActions.SERVICE_START, message="  GET  /docs - API documentation")

    logger.info(action=LogActions.SERVICE_START, message="Inventory Service startup complete!")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info(action=LogActions.SERVICE_START, message="Inventory Service shutting down...")


# For local development
if __name__ == "__main__":

    port = int(os.getenv("PORT", 8001))  # Different port from user-service (8000)
    host = os.getenv("HOST", "0.0.0.0")

    logger.info(action=LogActions.SERVICE_START, message=f"Starting server on {host}:{port}")
    logger.info(action=LogActions.SERVICE_START, message="Development Mode:")
    logger.info(action=LogActions.SERVICE_START, message="  - Auto-reload enabled")
    logger.info(action=LogActions.SERVICE_START, message="  - CORS configured for development")
    logger.info(action=LogActions.SERVICE_START, message="  - Detailed logging enabled")
    logger.info(action=LogActions.SERVICE_START, message="  - Sample data initialization on startup")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,  # Enable reload for development
        log_level="info"
    )