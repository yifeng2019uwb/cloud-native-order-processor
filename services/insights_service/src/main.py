"""
Insights Service - FastAPI Application Entry Point
"""
import os
import uvicorn
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from common.shared.logging import BaseLogger, LogAction, LoggerName
from controllers.health import router as health_router
from controllers.insights.portfolio_insights import router as insights_router
from api_info_enum import ServiceMetadata, ApiPaths, ApiTags
from constants import (
    RESPONSE_FIELD_SERVICE,
    RESPONSE_FIELD_VERSION,
    RESPONSE_FIELD_STATUS,
    RESPONSE_FIELD_TIMESTAMP,
    RESPONSE_FIELD_ENDPOINTS,
    RESPONSE_FIELD_DOCS,
    RESPONSE_FIELD_HEALTH,
    RESPONSE_FIELD_INSIGHTS,
    DEFAULT_SERVICE_PORT,
    SERVICE_PORT_ENV_VAR
)
from common.shared.constants.api_constants import HTTPStatus
from common.shared.constants.api_constants import ErrorMessages

from common.exceptions import (
    CNOPInternalServerException
)

# Initialize logger
logger = BaseLogger(LoggerName.INSIGHTS)

# Create FastAPI app
app = FastAPI(
    title=ServiceMetadata.NAME.value,
    description=ServiceMetadata.DESCRIPTION.value,
    version=ServiceMetadata.VERSION.value,
    docs_url=ApiPaths.DOCS.value,
    redoc_url=ApiPaths.REDOC.value
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, tags=[ApiTags.HEALTH.value])
app.include_router(insights_router, tags=[ApiTags.INSIGHTS.value])

# Root endpoint
@app.get("/")
def root():
    """Root endpoint - service information"""
    return {
        RESPONSE_FIELD_SERVICE: ServiceMetadata.NAME.value,
        RESPONSE_FIELD_VERSION: ServiceMetadata.VERSION.value,
        RESPONSE_FIELD_STATUS: ServiceMetadata.STATUS_RUNNING.value,
        RESPONSE_FIELD_TIMESTAMP: datetime.now(timezone.utc).isoformat(),
        RESPONSE_FIELD_ENDPOINTS: {
            RESPONSE_FIELD_DOCS: ApiPaths.DOCS.value,
            RESPONSE_FIELD_HEALTH: ApiPaths.HEALTH.value,
            RESPONSE_FIELD_INSIGHTS: ApiPaths.PORTFOLIO_INSIGHTS.value
        }
    }

# Custom exception handlers
@app.exception_handler(CNOPInternalServerException)
def internal_exception_handler(request, exc):
    logger.error(action=LogAction.ERROR, message=f"{ErrorMessages.INTERNAL_SERVER_ERROR}: {exc}")
    return JSONResponse(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content={"detail": str(exc)})

if __name__ == "__main__":
    port = int(os.getenv(SERVICE_PORT_ENV_VAR, str(DEFAULT_SERVICE_PORT)))
    uvicorn.run(app, host="0.0.0.0", port=port)
