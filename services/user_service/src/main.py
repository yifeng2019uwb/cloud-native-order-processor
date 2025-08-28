"""
FastAPI Application Entry Point - User Authentication Service
Path: services/user-service/src/main.py

This is the API layer entry point. It handles:
- API routing and middleware
- Exception handling
- Service configuration
- Environment variables loaded from services/.env
- Structured logging for K8s deployment
"""
import sys
import os
import json
import time
import uuid
import traceback
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError

# Import common exceptions (shared across services)
from common.exceptions.shared_exceptions import (
    CNOPInvalidCredentialsException,
    CNOPUserNotFoundException,
    CNOPInternalServerException
)
from user_exceptions.exceptions import CNOPUserValidationException

# Import other common exceptions
from common.exceptions import (
    # Database exceptions
    CNOPDatabaseOperationException,
    # Business logic exceptions
    CNOPInsufficientBalanceException
)

# Import user service specific exceptions
from user_exceptions.exceptions import (
    CNOPUserAlreadyExistsException
)

# Import our standardized logger
from common.shared.logging import BaseLogger, Loggers, LogActions

# Initialize our standardized logger
logger = BaseLogger(Loggers.USER)

# Load environment variables from services/.env
from dotenv import load_dotenv

# Find the services root directory (go up from user-service/src to services/)
services_root = Path(__file__).parent.parent.parent
env_file = services_root / ".env"

if env_file.exists():
    load_dotenv(env_file)
    logger.info(action=LogActions.SERVICE_START, message=f"Environment loaded from: {env_file}")
else:
    logger.warning(action=LogActions.ERROR, message=f"Environment file not found at: {env_file}")
    logger.info(action=LogActions.SERVICE_START, message="Continuing with system environment variables...")

# Initialize STS client for AWS role assumption
from common.aws.sts_client import STSClient
sts_client = STSClient()
logger.info(action=LogActions.SERVICE_START, message="STS client initialized for role assumption")

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
    """Logging middleware for K8s deployment"""

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
        "environment": "k8s"
    }

    logger.info(action=LogActions.REQUEST_START, message=json.dumps(log_entry))

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
            "environment": "k8s"
        }

        logger.info(action=LogActions.REQUEST_END, message=json.dumps(completion_entry))

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
            "environment": "k8s"
        }

        logger.error(action=LogActions.ERROR, message=json.dumps(error_entry))

        raise  # Re-raise the exception

# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Handle Pydantic validation errors"""
    logger.warning(action=LogActions.VALIDATION_ERROR, message=f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)}
    )

@app.exception_handler(CNOPUserValidationException)
async def user_validation_exception_handler(request, exc):
    """Handle user validation exceptions"""
    logger.warning(action=LogActions.VALIDATION_ERROR, message=f"User validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)}
    )

@app.exception_handler(CNOPUserAlreadyExistsException)
async def user_already_exists_exception_handler(request, exc):
    """Handle user already exists exceptions"""
    logger.warning(action=LogActions.ERROR, message=f"User already exists: {exc}")
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc)}
    )

@app.exception_handler(CNOPInvalidCredentialsException)
async def invalid_credentials_exception_handler(request, exc):
    """Handle invalid credentials exceptions"""
    logger.warning(action=LogActions.AUTH_FAILED, message=f"Invalid credentials: {exc}")
    return JSONResponse(
        status_code=401, # Changed from 422 to 401 as per RFC 7807
        content={"detail": str(exc)}
    )

@app.exception_handler(CNOPUserNotFoundException)
async def user_not_found_exception_handler(request, exc):
    """Handle user not found exceptions"""
    logger.warning(action=LogActions.ERROR, message=f"User not found: {exc}")

    # For login scenarios, treat UserNotFoundException as authentication failure (401)
    # For other scenarios, it would be resource not found (404)
    # We can determine this from the request path
    if "/auth/login" in str(request.url):
        return JSONResponse(
            status_code=401, # Changed from 422 to 401
            content={"detail": str(exc)}
        )
    else:
        return JSONResponse(
            status_code=404, # Changed from 422 to 404
            content={"detail": str(exc)}
        )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    logger.warning(action=LogActions.ERROR, message=f"HTTP exception: {exc}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(CNOPDatabaseOperationException)
async def database_operation_exception_handler(request, exc):
    """Handle database operation exceptions"""
    import traceback
    logger.error(action=LogActions.ERROR, message=f"Database operation exception: {exc}")
    logger.error(action=LogActions.ERROR, message=f"Exception type: {type(exc).__name__}")
    logger.error(action=LogActions.ERROR, message=f"Full traceback: {traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

@app.exception_handler(CNOPInsufficientBalanceException)
async def insufficient_balance_exception_handler(request, exc):
    """Handle insufficient balance exceptions"""
    logger.warning(action=LogActions.ERROR, message=f"Insufficient balance: {exc}")
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle all other exceptions"""
    import traceback
    logger.error(action=LogActions.ERROR, message=f"Global exception: {exc}")
    logger.error(action=LogActions.ERROR, message=f"Exception type: {type(exc).__name__}")
    logger.error(action=LogActions.ERROR, message=f"Full traceback: {traceback}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

    logger.info(action=LogActions.SERVICE_START, message="Exception handlers registered successfully")

# Import and include API routes
from controllers.auth.login import router as login_router
from controllers.auth.register import router as register_router
from controllers.auth.profile import router as profile_router
from controllers.auth.logout import router as logout_router
from controllers.balance import router as balance_router
from controllers.health import router as health_router

app.include_router(login_router, prefix="/auth", tags=["authentication"])
app.include_router(register_router, prefix="/auth", tags=["authentication"])
app.include_router(profile_router, prefix="/auth", tags=["authentication"])
app.include_router(logout_router, prefix="/auth", tags=["authentication"])
app.include_router(balance_router, tags=["balance"])
app.include_router(health_router, tags=["health"])

logger.info(action=LogActions.SERVICE_START, message="All API routes loaded successfully")

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
            "profile": "/auth/profile",
            "logout": "/auth/logout"
        },
        "environment": {
            "service": "user-service",
            "environment": os.getenv("ENVIRONMENT", "development")
        }
    }

# Add a simple endpoint to test logging
@app.get("/test-logging")
async def test_logging():
    """Endpoint to test logging"""
    logger.info(action=LogActions.REQUEST_START, message="Test logging endpoint called")

    return {
        "message": "Logging test completed",
        "environment": "k8s",
        "timestamp": datetime.utcnow().isoformat()
    }

# Enhanced startup event
@app.on_event("startup")
async def startup_event():
    """Startup event handler - API service initialization"""
    logger.info(action=LogActions.SERVICE_START, message="User Authentication Service starting up...")
    logger.info(action=LogActions.SERVICE_START, message=f"Environment: {os.getenv('ENVIRONMENT', 'development')}")

    # Log environment configuration
    logger.info(action=LogActions.SERVICE_START, message="API Service Configuration:")
    logger.info(action=LogActions.SERVICE_START, message=f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(action=LogActions.SERVICE_START, message=f"Services Root: {Path(__file__).parent.parent.parent}")
    logger.info(action=LogActions.SERVICE_START, message=f"Authentication: Gateway header-based (no JWT validation)")
    logger.info(action=LogActions.SERVICE_START, message=f"Service: user-authentication")
    logger.info(action=LogActions.SERVICE_START, message=f"Database: Accessed via DAO layer in common package")

    # Check required environment variables
    required_env_vars = {
        "USERS_TABLE": os.getenv("USERS_TABLE"),
        "ORDERS_TABLE": os.getenv("ORDERS_TABLE"),
        "INVENTORY_TABLE": os.getenv("INVENTORY_TABLE"),
        # "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY")  # Removed - no longer needed
    }

    logger.info(action=LogActions.SERVICE_START, message="Environment Variables:")
    for var_name, var_value in required_env_vars.items():
        if var_value:
            logger.info(action=LogActions.SERVICE_START, message=f"{var_name}: Configured")
        else:
            logger.warning(action=LogActions.ERROR, message=f"{var_name}: Missing")

    # Test API router availability
    try:
        import controllers.auth.login
        import controllers.auth.register
        import controllers.auth.profile
        import controllers.auth.logout
        import controllers.health
        logger.info(action=LogActions.SERVICE_START, message="API routes loaded successfully")
    except ImportError as e:
        logger.warning(action=LogActions.ERROR, message=f"Some API routes not available: {e}")

    # Log available endpoints
    logger.info(action=LogActions.SERVICE_START, message="Available endpoints:")
    logger.info(action=LogActions.SERVICE_START, message="  GET  /health - Basic health check (liveness probe)")
    logger.info(action=LogActions.SERVICE_START, message="  GET  /health/ready - Readiness probe")
    logger.info(action=LogActions.SERVICE_START, message="  GET  /health/db - Database health check")
    logger.info(action=LogActions.SERVICE_START, message="  POST /auth/register - User registration")
    logger.info(action=LogActions.SERVICE_START, message="  POST /auth/login - User login")
    logger.info(action=LogActions.SERVICE_START, message="  GET  /auth/profile - User profile")
    logger.info(action=LogActions.SERVICE_START, message="  PUT  /auth/profile - Update profile")
    logger.info(action=LogActions.SERVICE_START, message="  POST /auth/logout - User logout")
    logger.info(action=LogActions.SERVICE_START, message="  GET  /docs - API documentation")

    logger.info(action=LogActions.SERVICE_START, message="User Authentication Service startup complete!")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info(action=LogActions.SERVICE_START, message="User Authentication Service shutting down...")

# For local development
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    logger.info(action=LogActions.SERVICE_START, message=f"Starting server on {host}:{port}")
    logger.info(action=LogActions.SERVICE_START, message="Development Mode:")
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