"""
Health check controller for insights service
"""
from fastapi import APIRouter

from common.shared.constants.api_constants import HTTPStatus
from common.shared.constants.health_paths import HealthPaths
from common.shared.constants.service_names import ServiceNames, ServiceVersions
from common.shared.health.health_checks import HealthChecker, HealthCheckResponse
from common.shared.logging import BaseLogger, LoggerName

logger = BaseLogger(LoggerName.INSIGHTS)
router = APIRouter(tags=["health"])

health_checker = HealthChecker(ServiceNames.INSIGHTS_SERVICE.value, ServiceVersions.DEFAULT_VERSION)


@router.get(HealthPaths.HEALTH.value, status_code=HTTPStatus.OK)
def health_check() -> HealthCheckResponse:
    """Health check endpoint for Docker and Kubernetes probes."""
    return health_checker.health_check()
