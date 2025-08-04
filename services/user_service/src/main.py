"""
FastAPI Application Entry Point - User Authentication Service
Path: services/user-service/src/main.py

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

    # Find the services root directory (go up from user-service/src to services/)
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
    title="User Authentication Service",
    description="A cloud-native user authentication service",
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

    # Generate request ID for tracing
    request_id = str(uuid.uuid4())
    start_time = time.time()

    # Log request start
    log_entry = {
        "event": "request_start",
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "query_params": str(request.query_params) if request.query_params else None,
        "timestamp": datetime.utcnow().isoformat(),
        "service": "user-service",
        "environment": "lambda" if IS_LAMBDA else "k8s"
    }

    # In Lambda, use print() for CloudWatch; in K8s, use logger
    if IS_LAMBDA:
        print(json.dumps(log_entry))  # CloudWatch captures print() statements
    else:
        logger.info(json.dumps(log_entry))

    try:
        # Process the request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log successful completion
        completion_entry = {
            "event": "request_complete",
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_seconds": round(duration, 3),
            "timestamp": datetime.utcnow().isoformat(),
            "service": "user-service",
            "environment": "lambda" if IS_LAMBDA else "k8s"
        }

        if IS_LAMBDA:
            print(json.dumps(completion_entry))
        else:
            logger.info(json.dumps(completion_entry))

        return response

    except Exception as e:
        # Log errors
        error_entry = {
            "event": "request_error",
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "error": str(e),
            "duration_seconds": round(time.time() - start_time, 3),
            "timestamp": datetime.utcnow().isoformat(),
            "service": "user-service",
            "environment": "lambda" if IS_LAMBDA else "k8s"
        }

        if IS_LAMBDA:
            print(json.dumps(error_entry))
        else:
            logger.error(json.dumps(error_entry))

        raise  # Re-raise the exception

# Import common package exceptions
from common.exceptions import (
    DatabaseConnectionException,
    DatabaseOperationException,
    ConfigurationException,
    EntityValidationException,
    EntityAlreadyExistsException,
    EntityNotFoundException,
    UserValidationException,
    InvalidCredentialsException
)

# Import user service exceptions
from user_exceptions import (
    UserAlreadyExistsException,
    InternalServerException
)

# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Handle Pydantic validation errors"""
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

@app.exception_handler(UserValidationException)
async def user_validation_exception_handler(request, exc):
    """Handle user validation exceptions"""
    logger.warning(f"User validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)}
    )

@app.exception_handler(UserAlreadyExistsException)
async def user_already_exists_exception_handler(request, exc):
    """Handle user already exists exceptions"""
    logger.warning(f"User already exists: {exc}")
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc)}
    )

@app.exception_handler(InvalidCredentialsException)
async def invalid_credentials_exception_handler(request, exc):
    """Handle invalid credentials exceptions"""
    logger.warning(f"Invalid credentials: {exc}")
    return JSONResponse(
        status_code=401,
        content={"detail": str(exc)}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    logger.warning(f"HTTP exception: {exc}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle all other exceptions"""
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

logger.info("✅ Exception handlers registered successfully")

# Import and include API routers
try:
    from controllers.auth.login import router as login_router
    app.include_router(login_router, prefix="/auth", tags=["authentication"])
    logger.info("✅ Login routes loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ Login routes not available: {e}")

try:
    from controllers.auth.register import router as register_router
    app.include_router(register_router, prefix="/auth", tags=["authentication"])
    logger.info("✅ Registration routes loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ Registration routes not available: {e}")

try:
    from controllers.auth.profile import router as profile_router
    app.include_router(profile_router, prefix="/auth", tags=["authentication"])
    logger.info("✅ Profile routes loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ Profile routes not available: {e}")

try:
    from controllers.auth.logout import router as logout_router
    app.include_router(logout_router, prefix="/auth", tags=["authentication"])
    logger.info("✅ Logout routes loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ Logout routes not available: {e}")

try:
    from controllers.balance import router as balance_router
    app.include_router(balance_router, tags=["balance"])
    logger.info("✅ Balance routes loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ Balance routes not available: {e}")

try:
    from controllers.health import router as health_router
    app.include_router(health_router, tags=["health"])
    logger.info("✅ Health routes loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ Health routes not available: {e}")

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
            "register": "/auth/register",
            "login": "/auth/login",
            "profile": "/auth/me",
            "logout": "/auth/logout"
        },
        "environment": {
            "service": "user-service",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "lambda": IS_LAMBDA
        }
    }

# Add a simple endpoint to test logging
@app.get("/test-logging")
async def test_logging():
    """Endpoint to test CloudWatch logging"""
    logger.info("Test logging endpoint called")

    if IS_LAMBDA:
        print(json.dumps({
            "event": "test_endpoint",
            "message": "This is a test log from Lambda",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "user-service"
        }))

    return {
        "message": "Logging test completed",
        "environment": "lambda" if IS_LAMBDA else "k8s",
        "timestamp": datetime.utcnow().isoformat()
    }

# Enhanced startup event
@app.on_event("startup")
async def startup_event():
    """Startup event handler - API service initialization"""
    logger.info("🚀 User Authentication Service starting up...")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"Lambda Environment: {IS_LAMBDA}")

    # Log environment configuration
    logger.info("📊 API Service Configuration:")
    logger.info(f"  Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"  Services Root: {Path(__file__).parent.parent.parent}")
    logger.info(f"  JWT Secret configured: {'Yes' if os.getenv('JWT_SECRET_KEY') else 'No'}")
    logger.info(f"  Service: user-authentication")
    logger.info(f"  Database: Accessed via DAO layer in common package")

    # Check required environment variables
    required_env_vars = {
        "USERS_TABLE": os.getenv("USERS_TABLE"),
        "ORDERS_TABLE": os.getenv("ORDERS_TABLE"),
        "INVENTORY_TABLE": os.getenv("INVENTORY_TABLE"),
        "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY")
    }

    logger.info("🔧 Environment Variables:")
    for var_name, var_value in required_env_vars.items():
        if var_value:
            logger.info(f"  {var_name}: ✅ Configured")
        else:
            logger.warning(f"  {var_name}: ❌ Missing")

    # Test API router availability
    try:
        import controllers.auth.login
        import controllers.auth.register
        import controllers.auth.profile
        import controllers.auth.logout
        import controllers.health
        logger.info("✅ API routes loaded successfully")
    except ImportError as e:
        logger.warning(f"⚠️ Some API routes not available: {e}")

    # Log available endpoints
    logger.info("🎯 Available endpoints:")
    logger.info("  GET  /health - Basic health check (liveness probe)")
    logger.info("  GET  /health/ready - Readiness probe")
    logger.info("  GET  /health/db - Database health check")
    logger.info("  POST /auth/register - User registration")
    logger.info("  POST /auth/login - User login")
    logger.info("  GET  /auth/me - User profile")
    logger.info("  PUT  /auth/me - Update profile")
    logger.info("  POST /auth/logout - User logout")
    logger.info("  GET  /docs - API documentation")

    logger.info("✅ User Authentication Service startup complete!")

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
    logger.info("  - CloudWatch logging middleware active")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,  # Enable reload for development
        log_level="info"
    )