"""
Auth Service - FastAPI Application Entry Point
"""
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from common.shared.logging import BaseLogger, LoggerName, LogAction
from common.exceptions import CNOPInternalServerException
from common.auth.exceptions import CNOPAuthTokenExpiredException, CNOPAuthTokenInvalidException
from common.shared.constants.api_constants import HTTPStatus
from common.shared.constants.api_constants import ErrorMessages
from controllers.health import router as health_router
from controllers.validate import router as validate_router
from metrics import get_metrics_response
from api_info_enum import ServiceMetadata, ApiPaths, ApiTags, ApiResponseKeys, API_AUTH_PREFIX
from constants import (
    RESPONSE_FIELD_SERVICE, RESPONSE_FIELD_VERSION, RESPONSE_FIELD_STATUS, RESPONSE_FIELD_TIMESTAMP,
    RESPONSE_FIELD_ENDPOINTS, RESPONSE_FIELD_DOCS, RESPONSE_FIELD_HEALTH, RESPONSE_FIELD_VALIDATE, RESPONSE_FIELD_METRICS
)
from middleware import metrics_middleware

# Initialize logger
logger = BaseLogger(LoggerName.AUTH)

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
app.include_router(health_router, tags=[ApiTags.HEALTH.value])
app.include_router(validate_router, prefix=API_AUTH_PREFIX, tags=[ApiTags.INTERNAL.value])

# Add internal metrics endpoint
@app.get(ApiPaths.METRICS.value)
def internal_metrics():
    """Internal Prometheus metrics endpoint for monitoring"""
    return get_metrics_response()

# Custom exception handlers
@app.exception_handler(CNOPAuthTokenExpiredException)
def token_expired_exception_handler(request, exc):
    logger.warning(action=LogAction.AUTH_FAILED, message=f"Token expired: {exc}")
    return JSONResponse(status_code=HTTPStatus.UNAUTHORIZED, content={"detail": str(exc)})

@app.exception_handler(CNOPAuthTokenInvalidException)
def token_invalid_exception_handler(request, exc):
    logger.warning(action=LogAction.AUTH_FAILED, message=f"Token invalid: {exc}")
    return JSONResponse(status_code=HTTPStatus.UNAUTHORIZED, content={"detail": str(exc)})

@app.exception_handler(CNOPInternalServerException)
def internal_server_exception_handler(request, exc):
    logger.error(action=LogAction.ERROR, message=f"Internal server error: {exc}")
    return JSONResponse(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content={"detail": str(exc)})

@app.exception_handler(Exception)
def general_exception_handler(request, exc):
    logger.error(action=LogAction.ERROR, message=f"Unhandled error: {exc}")
    return JSONResponse(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content={"detail": ErrorMessages.INTERNAL_SERVER_ERROR})

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
            RESPONSE_FIELD_VALIDATE: ApiPaths.VALIDATE.value,
            RESPONSE_FIELD_METRICS: ApiPaths.METRICS.value
        }
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
