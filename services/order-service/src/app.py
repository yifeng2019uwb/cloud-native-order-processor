import sys
import os
# Add common package to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'common'))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from api.routes import health, orders, products, inventory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Order Processing API",
    description="A cloud-native order processing system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(orders.router)
app.include_router(products.router)
app.include_router(inventory.router)

@app.on_event("startup")
async def startup_event():
    logger.info("Order Service starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Order Service shutting down...")
    from database import db_manager
    await db_manager.close_pool()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)