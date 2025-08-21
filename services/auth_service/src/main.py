"""
Auth Service Main Application

FastAPI application entry point.
"""

from datetime import datetime, timezone
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import controllers
from controllers.health import router as health_router
from controllers.validate import router as validate_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
async def root():
    """Root endpoint with service information"""
    logger.info("Root endpoint accessed")

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
