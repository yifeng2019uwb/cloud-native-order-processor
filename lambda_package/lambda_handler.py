# lambda_package/lambda_handler.py
import sys
import os
import logging

# Configure logging for Lambda
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the services directory to Python path so we can import from it
lambda_package_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(lambda_package_dir)  # Go up one level to project root

# Add the actual path to your app.py
app_dir = os.path.join(project_root, "services", "order-service", "src")
sys.path.insert(0, app_dir)

# Also add common directory for shared imports
common_dir = os.path.join(project_root, "services", "common")
sys.path.insert(0, common_dir)

# Debug: Print the paths we're adding
logger.info(f"Lambda package dir: {lambda_package_dir}")
logger.info(f"Project root: {project_root}")
logger.info(f"App dir: {app_dir}")
logger.info(f"Looking for app.py at: {os.path.join(app_dir, 'app.py')}")
logger.info(f"App.py exists: {os.path.exists(os.path.join(app_dir, 'app.py'))}")

try:
    # Import your FastAPI app
    from app import app
    logger.info("Successfully imported FastAPI app")
except ImportError as e:
    logger.error(f"Failed to import FastAPI app: {e}")
    # Create a minimal fallback app
    from fastapi import FastAPI
    app = FastAPI()

    @app.get("/")
    async def fallback():
        return {"error": "Failed to import main app", "message": str(e)}

# Import mangum and wrap the FastAPI app
try:
    from mangum import Mangum
    handler = Mangum(app, lifespan="off")
    logger.info("Successfully created Lambda handler with mangum")
except ImportError as e:
    logger.error(f"Failed to import mangum: {e}")

    # Fallback handler if mangum is not available
    def handler(event, context):
        return {
            'statusCode': 500,
            'body': '{"error": "mangum not available"}'
        }

# Optional: Add some Lambda-specific configuration
def lambda_handler(event, context):
    """
    AWS Lambda entry point
    """
    logger.info(f"Lambda invoked with event: {event}")

    # You can add Lambda-specific logic here if needed
    # For example, setting environment-specific configurations

    return handler(event, context)