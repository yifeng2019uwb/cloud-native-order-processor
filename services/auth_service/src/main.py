"""
Auth Service Main Application

FastAPI application entry point.
"""

from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from common.shared.logging import BaseLogger, Loggers, LogActions
from controllers.health import router as health_router
from controllers.validate import router as validate_router

# Initialize logger
logger = BaseLogger(Loggers.AUTH)

# Create FastAPI app
app = FastAPI(
    title="Auth Service",
    description="Independent JWT validation service",
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

# Include routers
app.include_router(health_router)
app.include_router(validate_router)

# Root endpoint
@app.get("/")
def root():
    """Root endpoint with service information"""
    logger.info(action=LogActions.REQUEST_START, message="Root endpoint accessed")

    return {
        "service": "Auth Service",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "validate": "/internal/auth/validate"
        },
        "environment": {
            "service": "auth-service",
            "environment": "development"
        }
    }
