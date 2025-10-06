"""
Standardized Health Check Patterns

Provides common health check functionality for all microservices
to ensure consistent health monitoring and Kubernetes probe support.
"""

import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import HTTPException, status

from ...shared.logging import BaseLogger, LogActions, Loggers
from ...shared.constants.health_constants import HealthCheckConstants

logger = BaseLogger(Loggers.DATABASE, log_to_file=True)


class HealthCheckResponse:
    """Standardized health check response structure"""

    def __init__(
        self,
        service_name: str,
        version: str = "1.0.0",
        environment: Optional[str] = None
    ):
        self.service_name = service_name
        self.version = version
        self.environment = environment or os.getenv("ENVIRONMENT", HealthCheckConstants.DEFAULT_ENVIRONMENT)
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return {
            HealthCheckConstants.STATUS: HealthCheckConstants.STATUS_HEALTHY,
            HealthCheckConstants.SERVICE: self.service_name,
            HealthCheckConstants.VERSION: self.version,
            HealthCheckConstants.TIMESTAMP: self.timestamp,
            HealthCheckConstants.ENVIRONMENT: self.environment
        }


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
        self.response = HealthCheckResponse(service_name, version, self.environment)

    def basic_health_check(self) -> Dict[str, Any]:
        """
        Basic health check for Kubernetes liveness probe

        Lightweight check that only verifies the service is running.
        Does NOT check database connectivity to avoid probe failures.
        """
        return {
            **self.response.to_dict(),
            HealthCheckConstants.CHECKS: {
                HealthCheckConstants.API: HealthCheckConstants.OK,
                HealthCheckConstants.SERVICE: HealthCheckConstants.RUNNING
            }
        }

    def readiness_check(self) -> Dict[str, Any]:
        """
        Readiness check for Kubernetes readiness probe

        Checks if the service is ready to receive traffic.
        Includes database connectivity check.
        """
        try:
            # Test database connection
            db_healthy = get_database_health()

            if not db_healthy:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Database not ready"
                )

            return {
                **self.response.to_dict(),
                HealthCheckConstants.STATUS: HealthCheckConstants.READY,
                HealthCheckConstants.CHECKS: {
                    HealthCheckConstants.API: HealthCheckConstants.OK,
                    HealthCheckConstants.DATABASE: HealthCheckConstants.OK,
                    HealthCheckConstants.SERVICE: HealthCheckConstants.READY
                }
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                action=LogActions.ERROR,
                message=f"Readiness check failed: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service not ready"
            )

    def liveness_check(self) -> Dict[str, Any]:
        """
        Liveness check for Kubernetes liveness probe

        Checks if the service is alive and responding.
        No database calls - just basic service health.
        """
        return {
            **self.response.to_dict(),
            HealthCheckConstants.STATUS: HealthCheckConstants.ALIVE,
            HealthCheckConstants.CHECKS: {
                HealthCheckConstants.API: HealthCheckConstants.OK,
                HealthCheckConstants.SERVICE: HealthCheckConstants.ALIVE
            }
        }

    def database_health_check(self) -> Dict[str, Any]:
        """
        Database connectivity health check

        Specifically tests database connectivity and basic operations.
        Useful for monitoring and debugging database issues.
        """
        try:
            db_status = get_database_health()

            if not db_status:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Database unhealthy"
                )

            return {
                HealthCheckConstants.STATUS: HealthCheckConstants.STATUS_HEALTHY,
                HealthCheckConstants.SERVICE: f"{self.service_name}-database",
                HealthCheckConstants.TIMESTAMP: self.response.timestamp,
                HealthCheckConstants.DATABASE: {
                    HealthCheckConstants.STATUS: HealthCheckConstants.STATUS_HEALTHY,
                    HealthCheckConstants.CONNECTION: HealthCheckConstants.OK,
                    HealthCheckConstants.LAST_CHECK: self.response.timestamp
                }
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                action=LogActions.ERROR,
                message=f"Database health check failed: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database health check failed"
            )


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


def get_database_health() -> bool:
    """
    Check database health status

    Returns:
        bool: True if database is healthy, False otherwise
    """
    try:
        # Test DynamoDB connection
        from ...data.database.dynamodb_connection import get_dynamodb_manager
        health_ok = get_dynamodb_manager().health_check()
        return health_ok
    except Exception as e:
        logger.warning(
            action=LogActions.ERROR,
            message=f"Database health check failed: {e}"
        )
        return False