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
from constants import (
    METRICS_ENDPOINT, SERVICE_NAME, SERVICE_VERSION, STATUS_RUNNING,
    HTTP_STATUS_UNAUTHORIZED, HTTP_STATUS_CONFLICT, HTTP_STATUS_NOT_FOUND,
    HTTP_STATUS_UNPROCESSABLE_ENTITY, HTTP_STATUS_INTERNAL_SERVER_ERROR,
    API_PREFIX_AUTH, TAG_AUTHENTICATION, TAG_BALANCE, TAG_PORTFOLIO, TAG_ASSET_BALANCE, TAG_HEALTH,
    ENDPOINT_DOCS, ENDPOINT_REDOC, ENDPOINT_HEALTH, ENDPOINT_REGISTER, ENDPOINT_LOGIN,
    ENDPOINT_PROFILE, ENDPOINT_LOGOUT, API_ENDPOINT_BALANCE, API_ENDPOINT_DEPOSIT,
    API_ENDPOINT_WITHDRAW, API_ENDPOINT_TRANSACTIONS, API_ENDPOINT_PORTFOLIO,
    API_ENDPOINT_ASSET_BALANCE, ERROR_VALIDATION, ERROR_USER_EXISTS, ERROR_USER_NOT_FOUND,
    ERROR_INSUFFICIENT_BALANCE, ERROR_INVALID_CREDENTIALS, ERROR_INTERNAL_SERVER,
    RESPONSE_SERVICE, RESPONSE_VERSION, RESPONSE_STATUS, RESPONSE_TIMESTAMP, RESPONSE_ENDPOINTS,
    RESPONSE_DOCS, RESPONSE_HEALTH, RESPONSE_REGISTER, RESPONSE_LOGIN, RESPONSE_PROFILE,
    RESPONSE_LOGOUT, RESPONSE_BALANCE, RESPONSE_DEPOSIT, RESPONSE_WITHDRAW, RESPONSE_TRANSACTIONS,
    RESPONSE_PORTFOLIO, RESPONSE_ASSET_BALANCE
)
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
app.include_router(login_router, prefix=API_PREFIX_AUTH, tags=[TAG_AUTHENTICATION])
app.include_router(register_router, prefix=API_PREFIX_AUTH, tags=[TAG_AUTHENTICATION])
app.include_router(profile_router, prefix=API_PREFIX_AUTH, tags=[TAG_AUTHENTICATION])
app.include_router(logout_router, prefix=API_PREFIX_AUTH, tags=[TAG_AUTHENTICATION])
app.include_router(balance_router, tags=[TAG_BALANCE])
app.include_router(portfolio_router, tags=[TAG_PORTFOLIO])
app.include_router(asset_balance_router, tags=[TAG_ASSET_BALANCE])
app.include_router(health_router, tags=[TAG_HEALTH])

# Add internal metrics endpoint
@app.get(METRICS_ENDPOINT)
def internal_metrics():
    """Internal Prometheus metrics endpoint for monitoring"""
    return get_metrics_response()

# Custom exception handlers
@app.exception_handler(CNOPUserValidationException)
def validation_exception_handler(request, exc):
    logger.warning(action=LogActions.VALIDATION_ERROR, message=f"{ERROR_VALIDATION}: {exc}")
    return JSONResponse(status_code=HTTP_STATUS_UNPROCESSABLE_ENTITY, content={"detail": str(exc)})

@app.exception_handler(CNOPUserAlreadyExistsException)
def user_exists_exception_handler(request, exc):
    logger.warning(action=LogActions.VALIDATION_ERROR, message=f"{ERROR_USER_EXISTS}: {exc}")
    return JSONResponse(status_code=HTTP_STATUS_CONFLICT, content={"detail": str(exc)})

@app.exception_handler(CNOPUserNotFoundException)
def user_not_found_exception_handler(request, exc):
    logger.warning(action=LogActions.VALIDATION_ERROR, message=f"{ERROR_USER_NOT_FOUND}: {exc}")
    return JSONResponse(status_code=HTTP_STATUS_NOT_FOUND, content={"detail": str(exc)})

@app.exception_handler(CNOPInsufficientBalanceException)
def insufficient_balance_exception_handler(request, exc):
    logger.warning(action=LogActions.VALIDATION_ERROR, message=f"{ERROR_INSUFFICIENT_BALANCE}: {exc}")
    return JSONResponse(status_code=HTTP_STATUS_UNPROCESSABLE_ENTITY, content={"detail": str(exc)})

@app.exception_handler(CNOPInvalidCredentialsException)
def invalid_credentials_exception_handler(request, exc):
    logger.warning(action=LogActions.VALIDATION_ERROR, message=f"{ERROR_INVALID_CREDENTIALS}: {exc}")
    return JSONResponse(status_code=HTTP_STATUS_UNAUTHORIZED, content={"detail": str(exc)})

@app.exception_handler(CNOPInternalServerException)
def internal_server_exception_handler(request, exc):
    logger.error(action=LogActions.ERROR, message=f"{ERROR_INTERNAL_SERVER}: {exc}")
    return JSONResponse(status_code=HTTP_STATUS_INTERNAL_SERVER_ERROR, content={"detail": str(exc)})

@app.exception_handler(Exception)
def general_exception_handler(request, exc):
    logger.error(action=LogActions.ERROR, message=f"Unhandled error: {exc}")
    return JSONResponse(status_code=HTTP_STATUS_INTERNAL_SERVER_ERROR, content={"detail": ERROR_INTERNAL_SERVER})

# Root endpoint
@app.get("/")
def root():
    """Root endpoint with service information"""
    return {
        RESPONSE_SERVICE: SERVICE_NAME,
        RESPONSE_VERSION: SERVICE_VERSION,
        RESPONSE_STATUS: STATUS_RUNNING,
        RESPONSE_TIMESTAMP: datetime.now(timezone.utc).isoformat(),
        RESPONSE_ENDPOINTS: {
            RESPONSE_DOCS: ENDPOINT_DOCS,
            RESPONSE_HEALTH: ENDPOINT_HEALTH,
            RESPONSE_REGISTER: ENDPOINT_REGISTER,
            RESPONSE_LOGIN: ENDPOINT_LOGIN,
            RESPONSE_PROFILE: ENDPOINT_PROFILE,
            RESPONSE_LOGOUT: ENDPOINT_LOGOUT,
            RESPONSE_BALANCE: API_ENDPOINT_BALANCE,
            RESPONSE_DEPOSIT: API_ENDPOINT_DEPOSIT,
            RESPONSE_WITHDRAW: API_ENDPOINT_WITHDRAW,
            RESPONSE_TRANSACTIONS: API_ENDPOINT_TRANSACTIONS,
            RESPONSE_PORTFOLIO: API_ENDPOINT_PORTFOLIO,
            RESPONSE_ASSET_BALANCE: API_ENDPOINT_ASSET_BALANCE
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)