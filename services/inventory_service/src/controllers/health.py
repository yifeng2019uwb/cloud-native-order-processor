"""
Health check controller for inventory service
Path: services/inventory-service/src/controllers/health.py
"""
from fastapi import APIRouter
from typing import Dict, Any

# Import health components
from common.shared.health import HealthChecker, HealthCheckResponse
from common.shared.constants.http_status import HTTPStatus
from common.shared.constants.health_paths import HealthPaths
from api_info_enum import ApiTags, ApiPaths

# Import our standardized logger
from common.shared.logging import BaseLogger, Loggers, LogActions

# Initialize our standardized logger
logger = BaseLogger(Loggers.INVENTORY)
router = APIRouter(tags=[ApiTags.HEALTH.value])

# Create inventory service specific health checker
class InventoryServiceHealthChecker(HealthChecker):
    """Inventory service health checker"""

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

# Create inventory service health checker instance
health_checker = InventoryServiceHealthChecker("inventory-service", "1.0.0")


@router.get(HealthPaths.HEALTH.value)
def health_check():
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
