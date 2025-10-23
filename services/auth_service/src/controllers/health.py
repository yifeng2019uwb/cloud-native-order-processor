"""
Health Controller

Health check endpoint for Docker and Kubernetes.
"""

from fastapi import APIRouter
from typing import Dict, Any

from common.shared.health.health_checks import HealthChecker, HealthCheckResponse
from common.shared.constants.http_status import HTTPStatus
from common.shared.constants.health_paths import HealthPaths
from api_info_enum import ApiTags, ApiPaths, ServiceMetadata

router = APIRouter(tags=[ApiTags.HEALTH.value])

# Create auth service health checker instance
health_checker = HealthChecker(ServiceMetadata.NAME.value, ServiceMetadata.VERSION.value)


@router.get(HealthPaths.HEALTH.value, status_code=HTTPStatus.OK)
def health_check() -> HealthCheckResponse:
    """Health check endpoint for Docker and Kubernetes probes."""
    return health_checker.health_check()
