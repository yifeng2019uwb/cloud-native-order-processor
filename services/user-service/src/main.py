from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
import sys
from datetime import datetime

# Add common package to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "common", "src"))

# Set environment variables for DynamoDB (for development)
os.environ['ORDERS_TABLE'] = 'test-orders-table'
os.environ['INVENTORY_TABLE'] = 'test-inventory-table'
os.environ['REGION'] = 'us-west-2'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="User Authentication Service",
    description="A cloud-native user authentication service with JWT",
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


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Import and include routers
try:
    from routes.auth import router as auth_router
    app.include_router(auth_router)
    logger.info("Auth routes loaded successfully")
except ImportError as e:
    logger.error(f"Failed to import auth routes: {e}")

# Add these to your existing endpoints in main.py:

# Debug: Test import before the try/except
print("🔍 Testing auth import...")
try:
    import routes.auth
    print("✅ routes.auth imported successfully")
except Exception as e:
    print(f"❌ routes.auth import failed: {e}")
    import traceback
    traceback.print_exc()

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "User Authentication Service",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "docs": "/docs",
            "health": "/auth/health",
            "register": "/auth/register",
            "login": "/auth/login",
            "profile": "/auth/me"
        }
    }


# Main health check
@app.get("/health")
async def main_health_check():
    """Main application health check"""
    try:
        # You can add more sophisticated health checks here
        # e.g., database connectivity, external service checks
        return {
            "status": "healthy",
            "service": "user-auth-service",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "environment": os.getenv("ENVIRONMENT", "development"),
            "checks": {
                "database": "ok",  # Add actual DB check
                "jwt": "ok"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


# Startup event
@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("🚀 User Authentication Service starting up...")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"JWT Secret configured: {'Yes' if os.getenv('JWT_SECRET') else 'No (using default)'}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("👋 User Authentication Service shutting down...")


# For local development
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    logger.info(f"Starting server on {host}:{port}")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,  # Enable reload for development
        log_level="info"
    )