"""
User Service - FastAPI Application Entry Point
"""
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from common.shared.logging import BaseLogger, Loggers, LogActions
from controllers.auth.login import router as login_router
from controllers.auth.register import router as register_router
from controllers.auth.profile import router as profile_router
from controllers.auth.logout import router as logout_router
from controllers.balance import router as balance_router
from controllers.portfolio.portfolio_controller import router as portfolio_router
from controllers.portfolio.asset_balance_controller import router as asset_balance_router
from controllers.health import router as health_router
from metrics import get_metrics_response
from api_info_enum import ServiceMetadata, ApiPaths, ApiTags
from constants import (
    MSG_ERROR_USER_EXISTS,
    RESPONSE_FIELD_SERVICE, RESPONSE_FIELD_VERSION, RESPONSE_FIELD_STATUS, RESPONSE_FIELD_TIMESTAMP, RESPONSE_FIELD_ENDPOINTS,
    RESPONSE_FIELD_DOCS, RESPONSE_FIELD_HEALTH, RESPONSE_FIELD_REGISTER, RESPONSE_FIELD_LOGIN, RESPONSE_FIELD_PROFILE,
    RESPONSE_FIELD_LOGOUT, RESPONSE_FIELD_BALANCE, RESPONSE_FIELD_DEPOSIT, RESPONSE_FIELD_WITHDRAW, RESPONSE_FIELD_TRANSACTIONS,
    RESPONSE_FIELD_PORTFOLIO, RESPONSE_FIELD_ASSET_BALANCE
)
from common.shared.constants.http_status import HTTPStatus
from common.shared.constants.error_messages import ErrorMessages
from middleware import metrics_middleware

# Import custom exceptions
from user_exceptions import (
    CNOPUserAlreadyExistsException,
    CNOPUserValidationException
)

from common.exceptions import (
    CNOPUserNotFoundException,
    CNOPInsufficientBalanceException,
    CNOPInvalidCredentialsException,
    CNOPInternalServerException
)

# Initialize logger
logger = BaseLogger(Loggers.USER)

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

# Add metrics middleware
app.middleware("http")(metrics_middleware)

# Include routers
app.include_router(login_router, tags=[ApiTags.AUTHENTICATION.value])
app.include_router(register_router, tags=[ApiTags.AUTHENTICATION.value])
app.include_router(profile_router, tags=[ApiTags.AUTHENTICATION.value])
app.include_router(logout_router, tags=[ApiTags.AUTHENTICATION.value])
app.include_router(balance_router, tags=[ApiTags.BALANCE.value])
app.include_router(portfolio_router, tags=[ApiTags.PORTFOLIO.value])
app.include_router(asset_balance_router, tags=[ApiTags.ASSET_BALANCE.value])
app.include_router(health_router, tags=[ApiTags.HEALTH.value])

# Add internal metrics endpoint
@app.get(ApiPaths.METRICS.value)
def internal_metrics():
    """Internal Prometheus metrics endpoint for monitoring"""
    return get_metrics_response()

# Custom exception handlers
@app.exception_handler(CNOPUserValidationException)
def validation_exception_handler(request, exc):
    logger.warning(action=LogActions.VALIDATION_ERROR, message=f"{ErrorMessages.VALIDATION_ERROR}: {exc}")
    return JSONResponse(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, content={"detail": str(exc)})

@app.exception_handler(CNOPUserAlreadyExistsException)
def user_exists_exception_handler(request, exc):
    logger.warning(action=LogActions.VALIDATION_ERROR, message=f"{MSG_ERROR_USER_EXISTS}: {exc}")
    return JSONResponse(status_code=HTTPStatus.CONFLICT, content={"detail": str(exc)})

@app.exception_handler(CNOPUserNotFoundException)
def user_not_found_exception_handler(request, exc):
    logger.warning(action=LogActions.VALIDATION_ERROR, message=f"{ErrorMessages.USER_NOT_FOUND}: {exc}")
    return JSONResponse(status_code=HTTPStatus.NOT_FOUND, content={"detail": str(exc)})

@app.exception_handler(CNOPInsufficientBalanceException)
def insufficient_balance_exception_handler(request, exc):
    logger.warning(action=LogActions.VALIDATION_ERROR, message=f"{ErrorMessages.INSUFFICIENT_BALANCE}: {exc}")
    return JSONResponse(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, content={"detail": str(exc)})

@app.exception_handler(CNOPInvalidCredentialsException)
def invalid_credentials_exception_handler(request, exc):
    logger.warning(action=LogActions.VALIDATION_ERROR, message=f"{ErrorMessages.AUTHENTICATION_FAILED}: {exc}")
    return JSONResponse(status_code=HTTPStatus.UNAUTHORIZED, content={"detail": str(exc)})

@app.exception_handler(CNOPInternalServerException)
def internal_server_exception_handler(request, exc):
    logger.error(action=LogActions.ERROR, message=f"{ErrorMessages.INTERNAL_SERVER_ERROR}: {exc}")
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
            RESPONSE_FIELD_REGISTER: ApiPaths.REGISTER.value,
            RESPONSE_FIELD_LOGIN: ApiPaths.LOGIN.value,
            RESPONSE_FIELD_PROFILE: ApiPaths.PROFILE.value,
            RESPONSE_FIELD_LOGOUT: ApiPaths.LOGOUT.value,
            RESPONSE_FIELD_BALANCE: ApiPaths.BALANCE.value,
            RESPONSE_FIELD_DEPOSIT: ApiPaths.DEPOSIT.value,
            RESPONSE_FIELD_WITHDRAW: ApiPaths.WITHDRAW.value,
            RESPONSE_FIELD_TRANSACTIONS: ApiPaths.TRANSACTIONS.value,
            RESPONSE_FIELD_PORTFOLIO: ApiPaths.PORTFOLIO.value,
            RESPONSE_FIELD_ASSET_BALANCE: ApiPaths.ASSET_BALANCE.value
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)