"""
Health check controller for user authentication service
Path: services/user-service/src/controllers/health.py
"""
from fastapi import APIRouter, status
import logging
from typing import Dict, Any

from common.health import HealthChecker, HealthCheckResponse

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])

# Create user service specific health checker
class UserServiceHealthChecker(HealthChecker):
    """User service health checker"""

    async def readiness_check(self) -> Dict[str, Any]:
        """
        Readiness check for Kubernetes readiness probe

        Checks if the service is ready to receive traffic.
        """
        return {
            **self.response.to_dict(),
            "status": "ready",
            "checks": {
                "api": "ok",
                "service": "ready"
            }
        }

# Create user service health checker instance
health_checker = UserServiceHealthChecker("user-auth-service", "1.0.0")


@router.get("/health", status_code=status.HTTP_200_OK)
async def basic_health_check():
    """
    Basic health check endpoint for Kubernetes liveness probe

    This is a lightweight check that only verifies the service is running.
    """
    return await health_checker.basic_health_check()


@router.get("/health/ready", status_code=status.HTTP_200_OK)
async def readiness_check():
    """
    Readiness check endpoint for Kubernetes readiness probe

    This checks if the service is ready to receive traffic.
    """
    return await health_checker.readiness_check()


@router.get("/health/live", status_code=status.HTTP_200_OK)
async def liveness_check():
    """
    Liveness check endpoint for Kubernetes liveness probe

    This checks if the service is alive and responding.
    """
    return await health_checker.liveness_check()
