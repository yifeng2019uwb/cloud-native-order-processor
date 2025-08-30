"""
Auth Service - FastAPI Application Entry Point
"""
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from common.shared.logging import BaseLogger, Loggers, LogActions
from common.exceptions import CNOPInternalServerException
from common.auth.exceptions import CNOPAuthTokenExpiredException, CNOPAuthTokenInvalidException
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

# Custom exception handlers
@app.exception_handler(CNOPAuthTokenExpiredException)
def token_expired_exception_handler(request, exc):
    logger.warning(action=LogActions.AUTH_FAILED, message=f"Token expired: {exc}")
    return JSONResponse(status_code=401, content={"detail": str(exc)})

@app.exception_handler(CNOPAuthTokenInvalidException)
def token_invalid_exception_handler(request, exc):
    logger.warning(action=LogActions.AUTH_FAILED, message=f"Token invalid: {exc}")
    return JSONResponse(status_code=401, content={"detail": str(exc)})

@app.exception_handler(CNOPInternalServerException)
def internal_server_exception_handler(request, exc):
    logger.error(action=LogActions.ERROR, message=f"Internal server error: {exc}")
    return JSONResponse(status_code=500, content={"detail": str(exc)})

@app.exception_handler(Exception)
def general_exception_handler(request, exc):
    logger.error(action=LogActions.ERROR, message=f"Unhandled error: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

@app.get("/")
def root():
    """Root endpoint with service information"""
    return {
        "service": "Auth Service",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "validate": "/internal/auth/validate"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
