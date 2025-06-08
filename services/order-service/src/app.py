import sys
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Add common package to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "common"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Order Processing API",
    description="A cloud-native order processing system",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
try:
    from services.orders import router as orders_router
    app.include_router(orders_router)
except ImportError as e:
    logger.warning(f"Could not import orders router: {e}")

# Add a simple health check
@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.on_event("startup")
async def startup_event():
    logger.info("Order Service starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Order Service shutting down...")
    try:
        from database import db_manager
        await db_manager.close_pool()
    except ImportError:
        logger.warning("Could not import db_manager for cleanup")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)