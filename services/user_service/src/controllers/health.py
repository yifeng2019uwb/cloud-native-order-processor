"""
Health check controller for user authentication service
Path: services/user-service/src/controllers/health.py
"""
from fastapi import APIRouter, status
from typing import Dict, Any

from common.shared.health import HealthChecker, HealthCheckResponse
from common.shared.logging import BaseLogger, Loggers, LogActions

# Initialize our standardized logger
logger = BaseLogger(Loggers.USER)
router = APIRouter(tags=["health"])

# Create user service specific health checker
class UserServiceHealthChecker(HealthChecker):
    """User service health checker"""

    def readiness_check(self) -> Dict[str, Any]:
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
def basic_health_check():
    """
    Basic health check endpoint for Kubernetes liveness probe

    This is a lightweight check that only verifies the service is running.
    """
    return health_checker.basic_health_check()


@router.get("/health/ready", status_code=status.HTTP_200_OK)
def readiness_check():
    """
    Readiness check endpoint for Kubernetes readiness probe

    This checks if the service is ready to receive traffic.
    """
    return health_checker.readiness_check()


@router.get("/health/live", status_code=status.HTTP_200_OK)
def liveness_check():
    """
    Liveness check endpoint for Kubernetes liveness probe

    This checks if the service is alive and responding.
    """
    return health_checker.liveness_check()
