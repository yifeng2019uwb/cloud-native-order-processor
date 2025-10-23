"""
Order Service - FastAPI Application Entry Point
"""
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from common.shared.logging import BaseLogger, Loggers, LogActions
from common.exceptions import (
    CNOPAssetNotFoundException,
    CNOPUserNotFoundException,
    CNOPOrderNotFoundException,
    CNOPInternalServerException
)
from order_exceptions.exceptions import (
    CNOPOrderAlreadyExistsException,
    CNOPOrderServerException,
    CNOPOrderValidationException
)
from controllers.create_order import router as create_order_router
from controllers.get_order import router as get_order_router
from controllers.list_orders import router as list_orders_router
from controllers.asset_transaction import router as asset_transaction_router
from controllers.health import router as health_router
from metrics import get_metrics_response
from api_info_enum import ServiceMetadata, ApiPaths, ApiTags, ApiResponseKeys, API_PREFIX_ORDERS, API_PREFIX_ASSETS
from constants import (
    SERVICE_NAME, SERVICE_VERSION, SERVICE_DESCRIPTION, SERVICE_STATUS_RUNNING,
    RESPONSE_FIELD_SERVICE, RESPONSE_FIELD_VERSION, RESPONSE_FIELD_STATUS, RESPONSE_FIELD_TIMESTAMP,
    RESPONSE_FIELD_ENDPOINTS, RESPONSE_FIELD_DOCS, RESPONSE_FIELD_HEALTH, RESPONSE_FIELD_CREATE_ORDER,
    RESPONSE_FIELD_GET_ORDER, RESPONSE_FIELD_LIST_ORDERS, RESPONSE_FIELD_ASSET_TRANSACTIONS, RESPONSE_FIELD_METRICS
)
from common.shared.constants.api_constants import APIResponseKeys, ErrorMessages, HTTPStatus
from common.data.entities.entity_constants import OrderFields
from middleware import metrics_middleware

# Initialize logger
logger = BaseLogger(Loggers.ORDER)

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

# Include API routers
app.include_router(health_router, tags=[ApiTags.HEALTH.value])
app.include_router(create_order_router, prefix=API_PREFIX_ORDERS, tags=[ApiTags.ORDERS.value])
app.include_router(get_order_router, prefix=API_PREFIX_ORDERS, tags=[ApiTags.ORDERS.value])
app.include_router(list_orders_router, prefix=API_PREFIX_ORDERS, tags=[ApiTags.ORDERS.value])
app.include_router(asset_transaction_router, prefix=API_PREFIX_ASSETS, tags=[ApiTags.ASSET_TRANSACTIONS.value])

# Add internal metrics endpoint
@app.get(ApiPaths.METRICS.value)
def internal_metrics():
    """Internal Prometheus metrics endpoint for monitoring"""
    return get_metrics_response()

# Custom exception handlers
@app.exception_handler(CNOPOrderValidationException)
def order_validation_exception_handler(request, exc):
    logger.warning(action=LogActions.VALIDATION_ERROR, message=f"Order validation error: {exc}")
    return JSONResponse(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, content={"detail": str(exc)})

@app.exception_handler(CNOPOrderAlreadyExistsException)
def order_already_exists_exception_handler(request, exc):
    logger.warning(action=LogActions.VALIDATION_ERROR, message=f"Order already exists: {exc}")
    return JSONResponse(status_code=HTTPStatus.CONFLICT, content={"detail": str(exc)})

@app.exception_handler(CNOPUserNotFoundException)
def user_not_found_exception_handler(request, exc):
    logger.warning(action=LogActions.VALIDATION_ERROR, message=f"User not found: {exc}")
    return JSONResponse(status_code=HTTPStatus.NOT_FOUND, content={"detail": str(exc)})

@app.exception_handler(CNOPAssetNotFoundException)
def asset_not_found_exception_handler(request, exc):
    logger.warning(action=LogActions.VALIDATION_ERROR, message=f"Asset not found: {exc}")
    return JSONResponse(status_code=HTTPStatus.NOT_FOUND, content={"detail": str(exc)})

@app.exception_handler(CNOPOrderNotFoundException)
def order_not_found_exception_handler(request, exc):
    logger.warning(action=LogActions.VALIDATION_ERROR, message=f"Order not found: {exc}")
    return JSONResponse(status_code=HTTPStatus.NOT_FOUND, content={"detail": str(exc)})

@app.exception_handler(CNOPOrderServerException)
def order_server_exception_handler(request, exc):
    logger.error(action=LogActions.ERROR, message=f"Order server error: {exc}")
    return JSONResponse(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content={"detail": str(exc)})

@app.exception_handler(CNOPInternalServerException)
def internal_server_exception_handler(request, exc):
    logger.error(action=LogActions.ERROR, message=f"Internal server error: {exc}")
    return JSONResponse(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content={"detail": str(exc)})

@app.exception_handler(Exception)
def general_exception_handler(request, exc):
    logger.error(action=LogActions.ERROR, message=f"Unhandled error: {exc}")
    return JSONResponse(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content={"detail": ErrorMessages.INTERNAL_SERVER_ERROR})

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
                RESPONSE_FIELD_CREATE_ORDER: ApiPaths.ORDERS.value,
                RESPONSE_FIELD_GET_ORDER: ApiPaths.ORDER_BY_ID.value,
                RESPONSE_FIELD_LIST_ORDERS: ApiPaths.ORDERS.value,
                RESPONSE_FIELD_ASSET_TRANSACTIONS: ApiPaths.ASSET_TRANSACTIONS.value,
                RESPONSE_FIELD_METRICS: ApiPaths.METRICS.value
            }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)