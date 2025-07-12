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
import sys
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
from datetime import datetime
from pathlib import Path

# Load environment variables from services/.env
try:
    from dotenv import load_dotenv

    # Find the services root directory (go up from inventory-service/src to services/)
    services_root = Path(__file__).parent.parent.parent
    env_file = services_root / ".env"

    if env_file.exists():
        load_dotenv(env_file)
        logger = logging.getLogger(__name__)
        logger.info(f"✅ Environment loaded from: {env_file}")
    else:
        print(f"⚠️ Environment file not found at: {env_file}")
        print("Continuing with system environment variables...")

except ImportError:
    print("⚠️ python-dotenv not installed. Using system environment variables only.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

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
try:
    from metrics import metrics_middleware
    app.middleware("http")(metrics_middleware)
    logger.info("✅ Metrics middleware loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ Metrics middleware not available: {e}")

# Import and register secure exception handlers
try:
    from exceptions.secure_exceptions import (
        secure_validation_exception_handler,
        secure_general_exception_handler,
        secure_http_exception_handler
    )

    # Register secure exception handlers
    app.add_exception_handler(RequestValidationError, secure_validation_exception_handler)
    app.add_exception_handler(HTTPException, secure_http_exception_handler)
    app.add_exception_handler(Exception, secure_general_exception_handler)

    logger.info("✅ Secure exception handlers registered successfully")
except ImportError as e:
    logger.warning(f"⚠️ Could not import secure exception handlers: {e}")
    logger.info("Using fallback global exception handler")

    # Fallback global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        logger.error(f"Global exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

# Import and include API routers
try:
    from controllers.assets import router as assets_router
    app.include_router(assets_router, tags=["inventory"])
    logger.info("✅ Assets routes loaded successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import assets routes: {e}")
    logger.info("Continuing without assets endpoint...")

try:
    from controllers.health import router as health_router
    app.include_router(health_router, tags=["health"])
    logger.info("✅ Health routes loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ Health routes not available: {e}")

# Add metrics endpoint
try:
    from metrics import get_metrics
    from fastapi.responses import Response

    @app.get("/metrics")
    async def metrics():
        """Prometheus metrics endpoint"""
        return Response(
            content=get_metrics(),
            media_type="text/plain"
        )

    logger.info("✅ Metrics endpoint loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ Metrics endpoint not available: {e}")

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
async def main_health_check():
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
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


# Enhanced startup event
@app.on_event("startup")
async def startup_event():
    """Startup event handler - API service initialization"""
    logger.info("🚀 Inventory Service starting up...")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")

    # Log environment configuration
    logger.info("📊 API Service Configuration:")
    logger.info(f"  Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"  Services Root: {Path(__file__).parent.parent.parent}")
    logger.info(f"  Service: inventory-service")
    logger.info(f"  Database Region: {os.getenv('REGION', 'us-west-2')}")

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

    # Test API router availability
    try:
        import controllers.assets
        import controllers.health
        logger.info("✅ API routes loaded successfully")
    except ImportError as e:
        logger.warning(f"⚠️ Some API routes not available: {e}")

    # Initialize inventory data
    try:
        from data.init_inventory import startup_inventory_initialization
        logger.info("🎯 Initializing inventory data...")
        init_result = await startup_inventory_initialization()
        logger.info(f"📦 Data initialization: {init_result['status']}")
    except ImportError as e:
        logger.warning(f"⚠️ Could not import data initialization: {e}")
    except Exception as e:
        logger.error(f"❌ Data initialization failed: {e}")
        # Don't fail startup if data init fails - service can still run

    logger.info("🎯 Available endpoints:")
    logger.info("  GET  / - Service information")
    logger.info("  GET  /health - Main health check")
    logger.info("  GET  /health/ready - Readiness probe")
    logger.info("  GET  /health/live - Liveness probe")
    logger.info("  GET  /health/db - Database health")
    logger.info("  GET  /inventory/assets - List assets")
    logger.info("  GET  /inventory/assets/{id} - Get asset details")
    logger.info("  GET  /docs - API documentation")

    logger.info("✅ Inventory Service startup complete!")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("👋 Inventory Service shutting down...")


# For local development
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8001))  # Different port from user-service (8000)
    host = os.getenv("HOST", "0.0.0.0")

    logger.info(f"Starting server on {host}:{port}")
    logger.info("🔧 Development Mode:")
    logger.info("  - Auto-reload enabled")
    logger.info("  - CORS configured for development")
    logger.info("  - Detailed logging enabled")
    logger.info("  - Sample data initialization on startup")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,  # Enable reload for development
        log_level="info"
    )