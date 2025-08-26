"""
Health Controller

Health check endpoints for Kubernetes probes.
"""

from fastapi import APIRouter, status
from typing import Dict, Any

from common.shared.health import HealthChecker

router = APIRouter(tags=["health"])

# Create auth service health checker instance
health_checker = HealthChecker("auth-service", "1.0.0")


@router.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """Basic health check endpoint for Kubernetes liveness probe."""
    return health_checker.basic_health_check()


@router.get("/health/ready", status_code=status.HTTP_200_OK)
def readiness_check():
    """Readiness check endpoint for Kubernetes readiness probe."""
    return health_checker.readiness_check()


@router.get("/health/live", status_code=status.HTTP_200_OK)
def liveness_check():
    """Liveness check endpoint for Kubernetes liveness probe."""
    return health_checker.liveness_check()
