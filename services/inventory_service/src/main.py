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
from metrics import get_metrics_response
from api_info_enum import ServiceMetadata, ApiPaths, ApiTags, ApiResponseKeys, API_INVENTORY_PREFIX
from constants import (
    RESPONSE_FIELD_SERVICE, RESPONSE_FIELD_VERSION, RESPONSE_FIELD_STATUS, RESPONSE_FIELD_TIMESTAMP,
    RESPONSE_FIELD_ENDPOINTS, RESPONSE_FIELD_DOCS, RESPONSE_FIELD_HEALTH, RESPONSE_FIELD_ASSETS,
    RESPONSE_FIELD_ASSET_DETAIL, RESPONSE_FIELD_METRICS
)
from common.shared.constants.http_status import HTTPStatus
from common.shared.constants.error_messages import ErrorMessages
from middleware import metrics_middleware

# Initialize logger
logger = BaseLogger(Loggers.INVENTORY)

# Create FastAPI app
app = FastAPI(
    title=ServiceMetadata.TITLE.value,
    description=ServiceMetadata.DESCRIPTION.value,
    version=ServiceMetadata.VERSION.value,
    docs_url=ApiPaths.DOCS.value,
    redoc_url=ApiPaths.REDOC.value
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

# Include routers
app.include_router(assets_router, prefix=API_INVENTORY_PREFIX, tags=[ApiTags.INVENTORY.value])
app.include_router(health_router, tags=[ApiTags.HEALTH.value])

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
    return JSONResponse(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, content={"detail": str(exc)})

@app.exception_handler(CNOPAssetNotFoundException)
def asset_not_found_exception_handler(request, exc):
    logger.warning(action=LogActions.VALIDATION_ERROR, message=f"Asset not found: {exc}")
    return JSONResponse(status_code=HTTPStatus.NOT_FOUND, content={"detail": str(exc)})

@app.exception_handler(CNOPAssetAlreadyExistsException)
def asset_already_exists_exception_handler(request, exc):
    logger.warning(action=LogActions.VALIDATION_ERROR, message=f"Asset already exists: {exc}")
    return JSONResponse(status_code=HTTPStatus.CONFLICT, content={"detail": str(exc)})

@app.exception_handler(CNOPInventoryServerException)
def inventory_server_exception_handler(request, exc):
    logger.error(action=LogActions.ERROR, message=f"Inventory server error: {exc}")
    return JSONResponse(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content={"detail": str(exc)})

@app.exception_handler(CNOPInternalServerException)
def internal_server_exception_handler(request, exc):
    logger.error(action=LogActions.ERROR, message=f"Internal server error: {exc}")
    return JSONResponse(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content={"detail": str(exc)})

@app.exception_handler(Exception)
def general_exception_handler(request, exc):
    logger.error(action=LogActions.ERROR, message=f"Unhandled error: {exc}")
    return JSONResponse(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content={"detail": ErrorMessages.INTERNAL_SERVER_ERROR})

# Add internal metrics endpoint
@app.get(ApiPaths.METRICS.value)
def internal_metrics():
    """Internal Prometheus metrics endpoint for monitoring"""
    return get_metrics_response()

# Root endpoint
@app.get("/")
def root():
    """Root endpoint with service information"""
    return {
        RESPONSE_FIELD_SERVICE: ServiceMetadata.NAME.value,
        RESPONSE_FIELD_VERSION: ServiceMetadata.VERSION.value,
        RESPONSE_FIELD_STATUS: ServiceMetadata.STATUS_RUNNING.value,
        RESPONSE_FIELD_TIMESTAMP: datetime.now(timezone.utc).isoformat(),
        RESPONSE_FIELD_ENDPOINTS: {
            RESPONSE_FIELD_DOCS: ApiPaths.DOCS.value,
            RESPONSE_FIELD_HEALTH: ApiPaths.HEALTH.value,
            RESPONSE_FIELD_ASSETS: ApiPaths.ASSETS.value,
            RESPONSE_FIELD_ASSET_DETAIL: ApiPaths.ASSET_BY_ID.value,
            RESPONSE_FIELD_METRICS: ApiPaths.METRICS.value
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)