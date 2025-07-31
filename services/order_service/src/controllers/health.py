"""
Health check endpoints for Order Service
Path: services/order-service/src/controllers/health.py
"""
from fastapi import APIRouter, status
import logging
from typing import Dict, Any

from common.health import HealthChecker, HealthCheckResponse

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])

# Create order service specific health checker (no database dependencies)
class OrderServiceHealthChecker(HealthChecker):
    """Order service health checker without database dependencies"""

    async def readiness_check(self) -> Dict[str, Any]:
        """
        Readiness check for Kubernetes readiness probe

        Order service readiness check - no database dependencies.
        Only checks if the service is ready to receive traffic.
        """
        return {
            **self.response.to_dict(),
            "status": "ready",
            "checks": {
                "api": "ok",
                "service": "ready"
            }
        }

# Create health checker instance
health_checker = OrderServiceHealthChecker("order-service", "1.0.0")


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