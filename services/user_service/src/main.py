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
from controllers.health import router as health_router

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

# Include routers
app.include_router(login_router, prefix="/auth", tags=["authentication"])
app.include_router(register_router, prefix="/auth", tags=["authentication"])
app.include_router(profile_router, prefix="/auth", tags=["authentication"])
app.include_router(logout_router, prefix="/auth", tags=["authentication"])
app.include_router(balance_router, tags=["balance"])
app.include_router(health_router, tags=["health"])

# Custom exception handlers
@app.exception_handler(CNOPUserValidationException)
def validation_exception_handler(request, exc):
    logger.warning(action=LogActions.VALIDATION_ERROR, message=f"Validation error: {exc}")
    return JSONResponse(status_code=422, content={"detail": str(exc)})

@app.exception_handler(CNOPUserAlreadyExistsException)
def user_exists_exception_handler(request, exc):
    logger.warning(action=LogActions.VALIDATION_ERROR, message=f"User already exists: {exc}")
    return JSONResponse(status_code=409, content={"detail": str(exc)})

@app.exception_handler(CNOPUserNotFoundException)
def user_not_found_exception_handler(request, exc):
    logger.warning(action=LogActions.VALIDATION_ERROR, message=f"User not found: {exc}")
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@app.exception_handler(CNOPInsufficientBalanceException)
def insufficient_balance_exception_handler(request, exc):
    logger.warning(action=LogActions.VALIDATION_ERROR, message=f"Insufficient balance: {exc}")
    return JSONResponse(status_code=422, content={"detail": str(exc)})

@app.exception_handler(CNOPInvalidCredentialsException)
def invalid_credentials_exception_handler(request, exc):
    logger.warning(action=LogActions.VALIDATION_ERROR, message=f"Invalid credentials: {exc}")
    return JSONResponse(status_code=401, content={"detail": str(exc)})

@app.exception_handler(CNOPInternalServerException)
def internal_server_exception_handler(request, exc):
    logger.error(action=LogActions.ERROR, message=f"Internal server error: {exc}")
    return JSONResponse(status_code=500, content={"detail": str(exc)})

@app.exception_handler(Exception)
def general_exception_handler(request, exc):
    logger.error(action=LogActions.ERROR, message=f"Unhandled error: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

# Root endpoint
@app.get("/")
def root():
    """Root endpoint with service information"""
    return {
        "service": "User Authentication Service",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "register": "/auth/register",
            "login": "/auth/login",
            "profile": "/auth/profile",
            "logout": "/auth/logout",
            "balance": "/balance",
            "deposit": "/balance/deposit",
            "withdraw": "/balance/withdraw",
            "transactions": "/balance/transactions"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)