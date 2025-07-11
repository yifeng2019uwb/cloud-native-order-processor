"""
Health check controller for inventory service
Path: services/inventory-service/src/controllers/health.py
"""
from fastapi import APIRouter, Depends, status, HTTPException
import logging
from datetime import datetime, timezone
import os

# Import common DAO for database health check
from common.dao.asset_dao import AssetDAO
from common.database.dynamodb_connection import get_dynamodb, dynamodb_manager

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
        "service": "inventory-service",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "checks": {
            "api": "ok",
            "service": "running"
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
            "service": "inventory-service",
            "version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checks": {
                "api": "ok",
                "database": "ok",
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
async def database_health_check(asset_dao: AssetDAO = Depends(lambda: AssetDAO(None))):
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
            "service": "inventory-service-database",
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


@router.get("/health/live", status_code=status.HTTP_200_OK)
async def liveness_check():
    """
    Liveness check endpoint for Kubernetes liveness probe

    This is an alias for the basic health check.
    Kubernetes will restart the pod if this fails.
    """
    return await basic_health_check()


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
            asset_dao = AssetDAO(db_connection)

            # Test basic query operation
            assets = await asset_dao.get_all_assets(active_only=True)
            asset_count = len(assets)

            # Test individual asset lookup (if assets exist)
            sample_asset = None
            if assets:
                sample_asset = await asset_dao.get_asset_by_id(assets[0].asset_id)

            return {
                "status": "healthy",
                "connection": "ok",
                "operations": {
                    "list_assets": "ok",
                    "get_asset": "ok" if sample_asset else "no_data"
                },
                "statistics": {
                    "total_assets": asset_count,
                    "sample_asset_id": assets[0].asset_id if assets else None
                },
                "tables": {
                    "inventory_table": "accessible"
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


# Development/Debug endpoints

@router.get("/health/debug", status_code=status.HTTP_200_OK)
async def debug_info():
    """
    Debug information endpoint

    Provides detailed service information for debugging.
    Should be disabled in production.
    """
    try:
        db_status = await detailed_database_check()

        return {
            "service": "inventory-service",
            "version": "1.0.0",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "configuration": {
                "dynamodb_region": os.getenv("REGION", "us-west-2"),
                "users_table": os.getenv("USERS_TABLE"),
                "orders_table": os.getenv("ORDERS_TABLE"),
                "inventory_table": os.getenv("INVENTORY_TABLE")
            },
            "database": db_status,
            "endpoints": {
                "assets": [
                    "GET /inventory/assets",
                    "GET /inventory/assets/{asset_id}"
                ],
                "health": [
                    "GET /health",
                    "GET /health/ready",
                    "GET /health/live",
                    "GET /health/db",
                    "GET /health/debug"
                ]
            }
        }

    except Exception as e:
        logger.error(f"Debug info failed: {str(e)}")
        return {
            "service": "inventory-service",
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }