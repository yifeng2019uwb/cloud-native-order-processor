"""
FastAPI Application Entry Point - User Authentication Service
Path: cloud-native-order-processor/services/user-service/src/main.py

This is the API layer entry point. It should only handle:
- API routing and middleware
- Exception handling
- Service configuration
- Environment variables loaded from services/.env
- NOT database layer models or operations
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

    # Find the services root directory (go up from user-service/src to services/)
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

# FIXED: Import and include API routers with correct paths
try:
    from controllers.auth.registration import router as register_router
    app.include_router(register_router, prefix="/auth", tags=["authentication"])
    logger.info("✅ Registration routes loaded successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import registration routes: {e}")
    logger.info("Continuing without registration endpoint...")

try:
    from controllers.auth.login import router as login_router
    app.include_router(login_router, prefix="/auth", tags=["authentication"])
    logger.info("✅ Login routes loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ Login routes not available: {e}")

try:
    from controllers.auth.profile import router as profile_router
    app.include_router(profile_router, prefix="/auth", tags=["authentication"])
    logger.info("✅ Profile routes loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ Profile routes not available: {e}")

# NOTE: Logout router not implemented yet - simple JWT logout doesn't need server-side logic

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
            "auth_health": "/auth/register/health",
            "register": "/auth/register",
            "login": "/auth/login",
            "profile": "/auth/me"
        },
        "environment": {
            "service": "user-authentication",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "jwt_configured": bool(os.getenv('JWT_SECRET'))
        }
    }


# Main health check (API layer only - NO database calls)
@app.get("/health")
async def main_health_check():
    """Main application health check - API layer only, no database access"""
    try:
        health_status = {
            "status": "healthy",
            "service": "user-auth-service",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "environment": os.getenv("ENVIRONMENT", "development"),
            "checks": {
                "api": "ok",
                "jwt": "ok" if os.getenv('JWT_SECRET') else "using_default"
            }
        }

        # NO database connectivity check here - that should be in individual route health checks
        return health_status

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


# Enhanced startup event
@app.on_event("startup")
async def startup_event():
    """Startup event handler - API service initialization"""
    logger.info("🚀 User Authentication Service starting up...")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"JWT Secret configured: {'Yes' if os.getenv('JWT_SECRET') else 'No (using default)'}")

    # Log environment configuration (API service level only)
    logger.info("📊 API Service Configuration:")
    logger.info(f"  Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"  Services Root: {Path(__file__).parent.parent.parent}")
    logger.info(f"  JWT Secret: {'Configured' if os.getenv('JWT_SECRET') else 'Using default'}")
    logger.info(f"  Service: user-authentication")
    logger.info("  Database: Accessed via DAO layer in common package")

    # Test API router availability (not database)
    try:
        # Just test if we can import the router - no functional testing
        import controllers.auth.registration
        logger.info("✅ API routes loaded successfully")
    except ImportError as e:
        logger.warning(f"⚠️ Some API routes not available: {e}")

    logger.info("🎯 Available endpoints:")
    logger.info("  GET  /health - Main health check")
    logger.info("  POST /auth/register - User registration")
    logger.info("  POST /auth/login - User login")
    logger.info("  GET  /auth/me - User profile")
    logger.info("  PUT  /auth/me - Update profile")
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
    logger.info("  - API layer only (database accessed via DAO)")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,  # Enable reload for development
        log_level="info"
    )