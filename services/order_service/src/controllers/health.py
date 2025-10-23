"""
Health check endpoints for Order Service
Path: services/order-service/src/controllers/health.py
"""
from fastapi import APIRouter
from typing import Dict, Any

from common.shared.constants.api_constants import HTTPStatus
from common.shared.constants.health_paths import HealthPaths
from common.shared.constants.service_names import ServiceNames, ServiceVersions
from common.shared.health.health_checks import HealthChecker, HealthCheckResponse
from common.shared.logging import BaseLogger, Loggers

# Initialize our standardized logger
logger = BaseLogger(Loggers.ORDER)
router = APIRouter(tags=["health"])

# Create health checker instance
health_checker = HealthChecker(ServiceNames.ORDER_SERVICE.value, ServiceVersions.DEFAULT_VERSION)


@router.get(HealthPaths.HEALTH.value, status_code=HTTPStatus.OK)
def health_check() -> HealthCheckResponse:
    """Health check endpoint for Docker and Kubernetes probes."""
    return health_checker.health_check()