"""
Inventory Service - FastAPI Application Entry Point
"""
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
import asyncio

from common.shared.logging import BaseLogger, Loggers, LogActions
from common.exceptions import CNOPAssetNotFoundException, CNOPInternalServerException
from inventory_exceptions import (
    CNOPAssetAlreadyExistsException,
    CNOPInventoryServerException,
    CNOPAssetValidationException
)
from controllers.assets import router as assets_router
from controllers.health import router as health_router
from metrics import get_metrics

# Initialize logger
logger = BaseLogger(Loggers.INVENTORY)

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

# Include routers
app.include_router(assets_router)
app.include_router(health_router)

# Startup event - Initialize inventory data
@app.on_event("startup")
async def startup_event():
    """Initialize inventory data on service startup"""
    try:
        from data.init_inventory import startup_inventory_initialization
        logger.info(action=LogActions.SERVICE_START, message="Starting inventory initialization...")

        # Run initialization in background to not block startup
        asyncio.create_task(startup_inventory_initialization())

        logger.info(action=LogActions.SERVICE_START, message="Inventory initialization started in background")
    except Exception as e:
        logger.error(action=LogActions.ERROR, message=f"Failed to start inventory initialization: {e}")

# Custom exception handlers
@app.exception_handler(CNOPAssetValidationException)
def asset_validation_exception_handler(request, exc):
    logger.warning(action=LogActions.VALIDATION_ERROR, message=f"Asset validation error: {exc}")
    return JSONResponse(status_code=422, content={"detail": str(exc)})

@app.exception_handler(CNOPAssetNotFoundException)
def asset_not_found_exception_handler(request, exc):
    logger.warning(action=LogActions.VALIDATION_ERROR, message=f"Asset not found: {exc}")
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@app.exception_handler(CNOPAssetAlreadyExistsException)
def asset_already_exists_exception_handler(request, exc):
    logger.warning(action=LogActions.VALIDATION_ERROR, message=f"Asset already exists: {exc}")
    return JSONResponse(status_code=409, content={"detail": str(exc)})

@app.exception_handler(CNOPInventoryServerException)
def inventory_server_exception_handler(request, exc):
    logger.error(action=LogActions.ERROR, message=f"Inventory server error: {exc}")
    return JSONResponse(status_code=500, content={"detail": str(exc)})

@app.exception_handler(CNOPInternalServerException)
def internal_server_exception_handler(request, exc):
    logger.error(action=LogActions.ERROR, message=f"Internal server error: {exc}")
    return JSONResponse(status_code=500, content={"detail": str(exc)})

@app.exception_handler(Exception)
def general_exception_handler(request, exc):
    logger.error(action=LogActions.ERROR, message=f"Unhandled error: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

# Add metrics endpoint
@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint"""
    return Response(
        content=get_metrics(),
        media_type="text/plain"
    )

# Root endpoint
@app.get("/")
def root():
    """Root endpoint with service information"""
    return {
        "service": "Inventory Service",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "assets": "/inventory/assets",
            "asset_detail": "/inventory/assets/{asset_id}",
            "metrics": "/metrics"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)