"""
Health check controller for inventory service
Path: services/inventory-service/src/controllers/health.py
"""
from fastapi import APIRouter
from typing import Dict, Any

from common.shared.health.health_checks import HealthChecker, HealthCheckResponse
from common.shared.constants.api_constants import HTTPStatus
from common.shared.constants.health_paths import HealthPaths
from common.shared.constants.service_names import ServiceNames, ServiceVersions
from common.shared.logging import BaseLogger, Loggers
from api_info_enum import ApiTags

# Initialize our standardized logger
logger = BaseLogger(Loggers.INVENTORY)
router = APIRouter(tags=[ApiTags.HEALTH.value])

# Create inventory service health checker instance
health_checker = HealthChecker(ServiceNames.INVENTORY_SERVICE.value, ServiceVersions.DEFAULT_VERSION)


@router.get(HealthPaths.HEALTH.value, status_code=HTTPStatus.OK)
def health_check() -> HealthCheckResponse:
    """Health check endpoint for Docker and Kubernetes probes."""
    return health_checker.health_check()
