"""
Standardized Health Check Patterns

Provides common health check functionality for all microservices
to ensure consistent health monitoring and Kubernetes probe support.
"""

import os
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field

from ...shared.constants.health_constants import HealthCheckConstants


class HealthChecks(BaseModel):
    """Individual health check results"""

    api: str = Field(default=HealthCheckConstants.OK, description="API health status")
    service: str = Field(default=HealthCheckConstants.RUNNING, description="Service health status")


class HealthCheckResponse(BaseModel):
    """Standardized health check response structure"""

    status: str = Field(default=HealthCheckConstants.STATUS_HEALTHY, description="Health status")
    service: str = Field(..., description="Service name")
    version: str = Field(default="1.0.0", description="Service version")
    timestamp: str = Field(..., description="Check timestamp")
    environment: str = Field(..., description="Environment name")
    checks: HealthChecks = Field(default_factory=HealthChecks, description="Individual check statuses")


class HealthChecker:
    """Standardized health checker for microservices"""

    def __init__(
        self,
        service_name: str,
        version: str = "1.0.0",
        environment: Optional[str] = None
    ):
        self.service_name = service_name
        self.version = version
        self.environment = environment or os.getenv("ENVIRONMENT", HealthCheckConstants.DEFAULT_ENVIRONMENT)

    def health_check(self) -> HealthCheckResponse:
        """
        Single health check endpoint for Docker and Kubernetes

        Lightweight check that only verifies the service is running.
        Does NOT check database connectivity to avoid probe failures.
        """
        return HealthCheckResponse(
            service=self.service_name,
            version=self.version,
            timestamp=datetime.now(timezone.utc).isoformat(),
            environment=self.environment,
            checks=HealthChecks()
        )

    # Backward compatibility aliases
    def basic_health_check(self) -> HealthCheckResponse:
        return self.health_check()

    def readiness_check(self) -> HealthCheckResponse:
        return self.health_check()

    def liveness_check(self) -> HealthCheckResponse:
        return self.health_check()


def create_health_checker(service_name: str, version: str = "1.0.0") -> HealthChecker:
    """
    Factory function to create a health checker for a service

    Args:
        service_name: Name of the service
        version: Service version

    Returns:
        HealthChecker instance
    """
    return HealthChecker(service_name, version)