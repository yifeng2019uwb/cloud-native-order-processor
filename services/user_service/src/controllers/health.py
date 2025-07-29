"""
Health check controller for user authentication service
Path: services/user-service/src/controllers/health.py
"""
from fastapi import APIRouter, Depends, status, HTTPException
import logging
from datetime import datetime, timezone
import os

# Import common DAO for database health check
from common.dao.user_dao import UserDAO
from common.database.dynamodb_connection import dynamodb_manager

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def basic_health_check():
    """
    Basic health check endpoint for Kubernetes liveness probe

    This is a lightweight check that only verifies the service is running.
    Does NOT check database connectivity to avoid probe failures during DB maintenance.
    """
    return {
        "status": "healthy",
        "service": "user-auth-service",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "checks": {
            "api": "ok",
            "service": "running",
            "jwt": "ok" if os.getenv('JWT_SECRET_KEY') else "using_default"
        }
    }


@router.get("/health/ready", status_code=status.HTTP_200_OK)
async def readiness_check():
    """
    Readiness check endpoint for Kubernetes readiness probe

    This checks if the service is ready to receive traffic.
    Includes basic database connectivity check.
    """
    try:
        # Test database connection
        db_healthy = await check_database_health()

        if not db_healthy:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database not ready"
            )

        return {
            "status": "ready",
            "service": "user-auth-service",
            "version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checks": {
                "api": "ok",
                "database": "ok",
                "jwt": "ok" if os.getenv('JWT_SECRET_KEY') else "using_default",
                "service": "ready"
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not ready"
        )


@router.get("/health/db", status_code=status.HTTP_200_OK)
async def database_health_check(user_dao: UserDAO = Depends(lambda: UserDAO(None))):
    """
    Database connectivity health check

    This endpoint specifically tests database connectivity and basic operations.
    Useful for monitoring and debugging database issues.
    """
    try:
        db_status = await detailed_database_check()

        if db_status["status"] != "healthy":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Database unhealthy: {db_status.get('error', 'Unknown error')}"
            )

        return {
            "status": "healthy",
            "service": "user-auth-service-database",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database": db_status
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database health check failed"
        )


# Helper functions

async def check_database_health() -> bool:
    """
    Quick database health check

    Returns:
        bool: True if database is healthy, False otherwise
    """
    try:
        # Test DynamoDB connection
        health_ok = await dynamodb_manager.health_check()
        return health_ok

    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
        return False


async def detailed_database_check() -> dict:
    """
    Detailed database health check with statistics

    Returns:
        dict: Detailed database status information
    """
    try:
        # Test DynamoDB connection
        async with dynamodb_manager.get_connection() as db_connection:
            user_dao = UserDAO(db_connection)

            # Test basic table accessibility (lightweight)
            try:
                # Simple table scan to check connectivity (limit 1 for performance)
                response = user_dao.db.users_table.scan(Limit=1)
                user_count = response.get('Count', 0)
                user_operation = "ok"
            except Exception as e:
                logger.warning(f"User table scan test failed: {e}")
                user_count = 0
                user_operation = "failed"

            return {
                "status": "healthy",
                "connection": "ok",
                "operations": {
                    "user_query": user_operation
                },
                "statistics": {
                    "sample_users_found": user_count,
                    "table_accessible": "users_table"
                },
                "tables": {
                    "users_table": "accessible"
                },
                "last_check": datetime.now(timezone.utc).isoformat()
            }

    except Exception as e:
        logger.error(f"Detailed database check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "connection": "failed",
            "error": str(e),
            "last_check": datetime.now(timezone.utc).isoformat()
        }