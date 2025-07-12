"""
Lambda Handler with FastAPI and Mangum Bridge
"""
import json
import logging
import os
import sys
from datetime import datetime

# Configure logging for CloudWatch
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Global handler variable
handler = None

# Import FastAPI and Mangum
try:
    from fastapi import FastAPI, Request
    from mangum import Mangum
    import time
    import uuid

    # Create FastAPI app
    app = FastAPI(
        title="Order Processor API",
        description="Cloud Native Order Processor API",
        version="1.0.0"
    )

    # Add CloudWatch logging middleware
    @app.middleware("http")
    async def cloudwatch_logging_middleware(request: Request, call_next):
        request_id = str(uuid.uuid4())
        start_time = time.time()

        # Log request start
        logger.info(json.dumps({
            "event": "request_start",
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "timestamp": datetime.utcnow().isoformat(),
            "service": "order-processor-api",
            "environment": "lambda"
        }))

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log request completion
        logger.info(json.dumps({
            "event": "request_complete",
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_seconds": round(duration, 3),
            "timestamp": datetime.utcnow().isoformat(),
            "service": "order-processor-api",
            "environment": "lambda"
        }))

        return response

    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "Order Processor API",
            "environment": "lambda",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "running"
        }

    # Health endpoint
    @app.get("/health")
    async def health():
        return {
            "status": "healthy",
            "service": "Order Processor API",
            "environment": "lambda",
            "timestamp": datetime.utcnow().isoformat()
        }

    # Inventory service endpoints
    @app.get("/assets")
    async def get_assets():
        """Get all assets - Lambda endpoint"""
        return {
            "assets": [
                {
                    "asset_id": "BTC",
                    "name": "Bitcoin",
                    "symbol": "BTC",
                    "active": True,
                    "price": 45000.00
                },
                {
                    "asset_id": "ETH",
                    "name": "Ethereum",
                    "symbol": "ETH",
                    "active": True,
                    "price": 2800.00
                }
            ],
            "total_count": 2,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "lambda"
        }

    @app.get("/assets/{asset_id}")
    async def get_asset_by_id(asset_id: str):
        """Get specific asset - Lambda endpoint"""
        if asset_id.upper() == "BTC":
            return {
                "asset_id": "BTC",
                "name": "Bitcoin",
                "symbol": "BTC",
                "active": True,
                "price": 45000.00,
                "description": "Digital gold",
                "timestamp": datetime.utcnow().isoformat(),
                "source": "lambda"
            }
        elif asset_id.upper() == "ETH":
            return {
                "asset_id": "ETH",
                "name": "Ethereum",
                "symbol": "ETH",
                "active": True,
                "price": 2800.00,
                "description": "Smart contract platform",
                "timestamp": datetime.utcnow().isoformat(),
                "source": "lambda"
            }
        else:
            return {
                "error": "Asset not found",
                "asset_id": asset_id,
                "timestamp": datetime.utcnow().isoformat()
            }

    # User service endpoints
    @app.get("/auth/register")
    async def register():
        """User registration endpoint - Lambda"""
        return {
            "message": "User registration endpoint",
            "method": "GET",
            "timestamp": datetime.utcnow().isoformat(),
            "source": "lambda"
        }

    @app.post("/auth/register")
    async def register_post(request: Request):
        """User registration POST - Lambda"""
        try:
            body = await request.json()
            return {
                "message": "User registered successfully",
                "user_id": "user_123",
                "email": body.get("email", "unknown"),
                "timestamp": datetime.utcnow().isoformat(),
                "source": "lambda"
            }
        except:
            return {
                "message": "User registration endpoint",
                "method": "POST",
                "timestamp": datetime.utcnow().isoformat(),
                "source": "lambda"
            }

    @app.get("/auth/login")
    async def login():
        """User login endpoint - Lambda"""
        return {
            "message": "User login endpoint",
            "method": "GET",
            "timestamp": datetime.utcnow().isoformat(),
            "source": "lambda"
        }

    @app.post("/auth/login")
    async def login_post(request: Request):
        """User login POST - Lambda"""
        try:
            body = await request.json()
            return {
                "message": "User logged in successfully",
                "token": "jwt_token_123",
                "user_id": "user_123",
                "timestamp": datetime.utcnow().isoformat(),
                "source": "lambda"
            }
        except:
            return {
                "message": "User login endpoint",
                "method": "POST",
                "timestamp": datetime.utcnow().isoformat(),
                "source": "lambda"
            }

    # Create Mangum handler - this is the bridge between Lambda and FastAPI
    handler = Mangum(app, lifespan="off")
    logger.info("✅ FastAPI + Mangum Lambda handler created successfully")

except ImportError as import_error:
    error_msg = str(import_error)
    logger.error(f"❌ Failed to import FastAPI/Mangum: {error_msg}")

    # Fallback handler
    def fallback_handler(event, context):
        logger.error("Using fallback handler - FastAPI/Mangum not available")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                "error": "FastAPI/Mangum not available",
                "message": error_msg,
                "timestamp": datetime.utcnow().isoformat()
            })
        }

    handler = fallback_handler

def lambda_handler(event, context):
    """
    AWS Lambda entry point - Mangum bridges this to FastAPI
    """
    logger.info(f"🚀 Lambda invoked: {context.function_name}")
    logger.info(f"📊 Event type: {event.get('httpMethod', 'unknown')}")
    logger.info(f"🛣️ Path: {event.get('path', 'unknown')}")

    try:
        if handler is None:
            raise Exception("Handler not initialized")

        # Mangum handles the conversion between Lambda event and FastAPI
        result = handler(event, context)
        logger.info("✅ Lambda execution completed successfully")
        return result
    except Exception as error:
        logger.error(f"❌ Lambda execution failed: {str(error)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                "error": "Internal server error",
                "message": str(error),
                "timestamp": datetime.utcnow().isoformat()
            })
        }