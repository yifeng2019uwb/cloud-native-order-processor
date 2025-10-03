"""
Health check endpoints for Order Service
Path: services/order-service/src/controllers/health.py
"""
from fastapi import APIRouter
from common.shared.constants.http_status import HTTPStatus
from common.shared.constants.health_paths import HealthPaths
from typing import Dict, Any

from common.shared.health import HealthChecker, HealthCheckResponse
from common.shared.logging import BaseLogger, Loggers, LogActions

# Initialize our standardized logger
logger = BaseLogger(Loggers.ORDER)
router = APIRouter(tags=["health"])

# Create order service specific health checker (no database dependencies)
class OrderServiceHealthChecker(HealthChecker):
    """Order service health checker without database dependencies"""

    def readiness_check(self) -> Dict[str, Any]:
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


@router.get(HealthPaths.HEALTH.value, status_code=HTTPStatus.OK)
def basic_health_check():
    """
    Basic health check endpoint for Kubernetes liveness probe

    This is a lightweight check that only verifies the service is running.
    """
    return health_checker.basic_health_check()


@router.get(HealthPaths.HEALTH_READY.value, status_code=HTTPStatus.OK)
def readiness_check():
    """
    Readiness check endpoint for Kubernetes readiness probe

    This checks if the service is ready to receive traffic.
    """
    return health_checker.readiness_check()


@router.get(HealthPaths.HEALTH_LIVE.value, status_code=HTTPStatus.OK)
def liveness_check():
    """
    Liveness check endpoint for Kubernetes liveness probe

    This checks if the service is alive and responding.
    """
    return health_checker.liveness_check()