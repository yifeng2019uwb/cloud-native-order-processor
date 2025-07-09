from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
import os
import sys
from datetime import datetime

# Add common package to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "common", "src"))

# Set environment variables for DynamoDB (for development and Lambda compatibility)
os.environ['ORDERS_TABLE'] = os.getenv('ORDERS_TABLE', 'test-orders-table')
os.environ['INVENTORY_TABLE'] = os.getenv('INVENTORY_TABLE', 'test-inventory-table')
os.environ['USERS_TABLE'] = os.getenv('USERS_TABLE', 'test-users-table')  # Added for new registration
os.environ['REGION'] = os.getenv('AWS_REGION', 'us-west-2')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="User Authentication Service",
    description="A cloud-native user authentication service with JWT",
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

# Import and register secure exception handlers
try:
    from exceptions.internal_exceptions import InternalAuthError
    from exceptions.secure_exceptions import (
        secure_internal_exception_handler,
        secure_validation_exception_handler,
        secure_general_exception_handler
    )

    # Register secure exception handlers
    app.add_exception_handler(InternalAuthError, secure_internal_exception_handler)
    app.add_exception_handler(RequestValidationError, secure_validation_exception_handler)
    app.add_exception_handler(Exception, secure_general_exception_handler)

    logger.info("Secure exception handlers registered successfully")
except ImportError as e:
    logger.warning(f"Could not import secure exception handlers: {e}")
    logger.info("Using fallback global exception handler")

    # Fallback global exception handler (your existing one)
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        logger.error(f"Global exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

# Import and include new registration router
try:
    from src.routes.auth.register import router as register_router
    app.include_router(register_router, prefix="/auth", tags=["authentication"])
    logger.info("New registration routes loaded successfully")
except ImportError as e:
    logger.error(f"Failed to import new registration routes: {e}")
    logger.info("Continuing without new registration endpoint...")

# Import and include existing auth routers (keep your existing functionality)
try:
    from src.routes.auth import router as auth_router
    app.include_router(auth_router)
    logger.info("Existing auth routes loaded successfully")
except ImportError as e:
    logger.error(f"Failed to import existing auth routes: {e}")
    logger.info("No existing auth routes found - this is normal for new setup")

# Debug: Test imports for troubleshooting
print("🔍 Testing imports...")
try:
    # Test new registration import
    from src.routes.auth.register import router
    print("✅ New registration router imported successfully")
except Exception as e:
    print(f"❌ New registration router import failed: {e}")

try:
    # Test existing auth import
    import src.routes.auth
    print("✅ Existing routes.auth imported successfully")
except Exception as e:
    print(f"❌ Existing routes.auth import failed: {e}")

try:
    # Test database dependencies
    from src.routes.auth.dependencies import get_user_dao, get_db_connection
    print("✅ Database dependencies imported successfully")
except Exception as e:
    print(f"❌ Database dependencies import failed: {e}")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "User Authentication Service",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "auth_health": "/auth/health",
            "register": "/auth/register",
            "register_health": "/auth/register/health",
            "login": "/auth/login",
            "profile": "/auth/me"
        },
        "environment": {
            "users_table": os.getenv('USERS_TABLE'),
            "orders_table": os.getenv('ORDERS_TABLE'),
            "inventory_table": os.getenv('INVENTORY_TABLE'),
            "region": os.getenv('REGION')
        }
    }


# Main health check
@app.get("/health")
async def main_health_check():
    """Main application health check"""
    try:
        # Enhanced health check with database connectivity
        health_status = {
            "status": "healthy",
            "service": "user-auth-service",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "environment": os.getenv("ENVIRONMENT", "development"),
            "checks": {
                "database": "checking...",
                "jwt": "ok",
                "tables": {
                    "users": os.getenv('USERS_TABLE'),
                    "orders": os.getenv('ORDERS_TABLE'),
                    "inventory": os.getenv('INVENTORY_TABLE')
                }
            }
        }

        # Test database connectivity
        try:
            from src.routes.auth.dependencies import get_db_connection
            db_connection = await get_db_connection()
            health_status["checks"]["database"] = "ok"
            logger.debug("Database connectivity check passed")
        except Exception as db_error:
            health_status["checks"]["database"] = f"error: {str(db_error)}"
            health_status["status"] = "degraded"
            logger.warning(f"Database connectivity check failed: {db_error}")

        return health_status

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


# Enhanced startup event
@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("🚀 User Authentication Service starting up...")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"JWT Secret configured: {'Yes' if os.getenv('JWT_SECRET') else 'No (using default)'}")

    # Log table configurations
    logger.info("📊 Database Tables Configuration:")
    logger.info(f"  Users Table: {os.getenv('USERS_TABLE')}")
    logger.info(f"  Orders Table: {os.getenv('ORDERS_TABLE')}")
    logger.info(f"  Inventory Table: {os.getenv('INVENTORY_TABLE')}")
    logger.info(f"  Region: {os.getenv('REGION')}")

    # Test critical imports
    try:
        from src.routes.auth.dependencies import get_user_dao
        logger.info("✅ Registration dependencies loaded successfully")
    except ImportError as e:
        logger.warning(f"⚠️ Registration dependencies not available: {e}")

    logger.info("🎯 Available endpoints:")
    logger.info("  GET  /health - Main health check")
    logger.info("  POST /auth/register - User registration (new)")
    logger.info("  GET  /auth/register/health - Registration service health")
    logger.info("  GET  /docs - API documentation")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("👋 User Authentication Service shutting down...")


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

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,  # Enable reload for development
        log_level="info"
    )