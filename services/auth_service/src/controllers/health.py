"""
Health Controller

Health check endpoints for Kubernetes probes.
"""

from fastapi import APIRouter
from typing import Dict, Any

from common.shared.health import HealthChecker
from common.shared.constants.http_status import HTTPStatus
from common.shared.constants.health_paths import HealthPaths
from api_info_enum import ApiTags, ApiPaths, ServiceMetadata

router = APIRouter(tags=[ApiTags.HEALTH.value])

# Create auth service health checker instance
health_checker = HealthChecker(ServiceMetadata.NAME.value, ServiceMetadata.VERSION.value)


@router.get(HealthPaths.HEALTH.value, status_code=HTTPStatus.OK)
def health_check():
    """Basic health check endpoint for Kubernetes liveness probe."""
    return health_checker.basic_health_check()


@router.get(HealthPaths.HEALTH_READY.value, status_code=HTTPStatus.OK)
def readiness_check():
    """Readiness check endpoint for Kubernetes readiness probe."""
    return health_checker.readiness_check()


@router.get(HealthPaths.HEALTH_LIVE.value, status_code=HTTPStatus.OK)
def liveness_check():
    """Liveness check endpoint for Kubernetes liveness probe."""
    return health_checker.liveness_check()
