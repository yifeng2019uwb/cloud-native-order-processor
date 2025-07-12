# lambda_package/lambda_handler.py
import sys
import os
import logging
import json
from datetime import datetime

# Configure logging for CloudWatch FIRST (before any imports)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout  # Ensure logs go to stdout for CloudWatch
)
logger = logging.getLogger(__name__)

# Add the services directory to Python path so we can import from it
lambda_package_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(lambda_package_dir)  # Go up one level to project root

# Add the actual path to your main.py
app_dir = os.path.join(project_root, "services", "user-service", "src")
sys.path.insert(0, app_dir)

# Also add common directory for shared imports
common_dir = os.path.join(project_root, "services", "common")
sys.path.insert(0, common_dir)

# Debug: Print the paths we're adding
logger.info(f"Lambda package dir: {lambda_package_dir}")
logger.info(f"Project root: {project_root}")
logger.info(f"App dir: {app_dir}")
logger.info(f"Looking for main.py at: {os.path.join(app_dir, 'main.py')}")
logger.info(f"Main.py exists: {os.path.exists(os.path.join(app_dir, 'main.py'))}")

# Log environment variables for debugging
logger.info(f"Environment variables:")
logger.info(f"ORDERS_TABLE: {os.environ.get('ORDERS_TABLE')}")
logger.info(f"INVENTORY_TABLE: {os.environ.get('INVENTORY_TABLE')}")
logger.info(f"USERS_TABLE: {os.environ.get('USERS_TABLE')}")

try:
    # Import your FastAPI app
    from main import app
    logger.info("Successfully imported FastAPI app")

    # Add CloudWatch logging middleware to FastAPI
    from fastapi import Request, Response
    import time
    import uuid

    @app.middleware("http")
    async def cloudwatch_logging_middleware(request: Request, call_next):
        # Generate request ID for tracing
        request_id = str(uuid.uuid4())
        start_time = time.time()

        # Log request start
        logger.info(json.dumps({
            "event": "request_start",
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "timestamp": datetime.utcnow().isoformat(),
            "service": "user-service"
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
            "service": "user-service",
            "environment": "lambda"
        }))

        return response

    logger.info("Added CloudWatch logging middleware to FastAPI")

except ImportError as e:
    logger.error(f"Failed to import FastAPI app: {e}")
    # Create a minimal fallback app
    from fastapi import FastAPI
    app = FastAPI()

    @app.get("/")
    async def fallback():
        logger.error("Using fallback app due to import error")
        return {"error": "Failed to import main app", "message": str(e)}

    @app.get("/health")
    async def health():
        logger.info("Health check called on fallback app")
        return {
            "status": "healthy",
            "service": "Order Processor API",
            "environment": os.environ.get('ENVIRONMENT', 'dev'),
            "note": "fallback_app",
            "tables": {
                "orders": os.environ.get('ORDERS_TABLE'),
                "inventory": os.environ.get('INVENTORY_TABLE'),
                "users": os.environ.get('USERS_TABLE')
            }
        }

# Import mangum and wrap the FastAPI app
try:
    from mangum import Mangum
    # Configure mangum with logging
    handler = Mangum(app, lifespan="off")
    logger.info("Successfully created Lambda handler with mangum")
except ImportError as e:
    logger.error(f"Failed to import mangum: {e}")

    # Fallback handler if mangum is not available
    def handler(event, context):
        logger.error("Using fallback handler - mangum not available")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': '{"error": "mangum not available"}'
        }

def lambda_handler(event, context):
    """
    AWS Lambda entry point
    This is the function that Lambda calls (specified in Terraform as lambda_handler.lambda_handler)
    """
    logger.info(f"Lambda function invoked")
    logger.info(f"Event type: {event.get('httpMethod', 'unknown')}")
    logger.info(f"Path: {event.get('path', 'unknown')}")

    # Log the available environment variables
    logger.info(f"Environment check - ORDERS_TABLE: {os.environ.get('ORDERS_TABLE')}")

    try:
        result = handler(event, context)
        logger.info(f"Lambda execution completed successfully")
        return result
    except Exception as e:
        logger.error(f"Lambda execution failed: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                "error": "Internal server error",
                "message": str(e)
            })
        }