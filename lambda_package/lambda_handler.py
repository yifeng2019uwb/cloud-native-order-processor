"""
Simple Lambda Handler for API Gateway Testing
Separate from existing backend services
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

# Import FastAPI and Mangum
try:
    from fastapi import FastAPI, Request
    from mangum import Mangum
    import time
    import uuid

    # Create simple FastAPI app (separate from existing services)
    app = FastAPI(
        title="API Gateway Test",
        description="Simple Lambda API for testing",
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
            "service": "api-gateway-test",
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
            "service": "api-gateway-test",
            "environment": "lambda"
        }))

        return response

    # Simple test endpoints
    @app.get("/")
    async def root():
        return {
            "message": "API Gateway Test - Lambda",
            "environment": "lambda",
            "timestamp": datetime.utcnow().isoformat(),
            "note": "This is separate from your existing services"
        }

    @app.get("/health")
    async def health():
        return {
            "status": "healthy",
            "service": "API Gateway Test",
            "environment": "lambda",
            "timestamp": datetime.utcnow().isoformat()
        }

    @app.get("/test")
    async def test():
        return {
            "message": "Lambda API Gateway test working!",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "api-gateway-test"
        }

    @app.get("/info")
    async def info():
        return {
            "service": "API Gateway Test Lambda",
            "environment": "lambda",
            "timestamp": datetime.utcnow().isoformat(),
            "note": "Your existing services run separately on localhost:8000, 8001"
        }

    # Create Mangum handler
    handler = Mangum(app, lifespan="off")
    logger.info("✅ API Gateway Test Lambda handler created successfully")

except ImportError as e:
    logger.error(f"❌ Failed to import FastAPI/Mangum: {e}")

    # Fallback handler
    def handler(event, context):
        logger.error("Using fallback handler - FastAPI/Mangum not available")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                "error": "FastAPI/Mangum not available",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
        }

def lambda_handler(event, context):
    """
    AWS Lambda entry point for API Gateway testing
    Separate from existing backend services
    """
    logger.info(f"🚀 API Gateway Test Lambda invoked: {context.function_name}")
    logger.info(f"📊 Event type: {event.get('httpMethod', 'unknown')}")
    logger.info(f"🛣️ Path: {event.get('path', 'unknown')}")

    try:
        result = handler(event, context)
        logger.info("✅ Lambda execution completed successfully")
        return result
    except Exception as e:
        logger.error(f"❌ Lambda execution failed: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                "error": "Internal server error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
        }