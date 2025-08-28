"""
Standardized Health Check Patterns

Provides common health check functionality for all microservices
to ensure consistent health monitoring and Kubernetes probe support.
"""

from ...shared.logging import BaseLogger, Loggers, LogActions
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from fastapi import HTTPException, status

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
        self.environment = environment or os.getenv("ENVIRONMENT", "development")
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return {
            "status": "healthy",
            "service": self.service_name,
            "version": self.version,
            "timestamp": self.timestamp,
            "environment": self.environment
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
        self.environment = environment or os.getenv("ENVIRONMENT", "development")
        self.response = HealthCheckResponse(service_name, version, self.environment)

    def basic_health_check(self) -> Dict[str, Any]:
        """
        Basic health check for Kubernetes liveness probe

        Lightweight check that only verifies the service is running.
        Does NOT check database connectivity to avoid probe failures.
        """
        return {
            **self.response.to_dict(),
            "checks": {
                "api": "ok",
                "service": "running"
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
                "status": "ready",
                "checks": {
                    "api": "ok",
                    "database": "ok",
                    "service": "ready"
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
            "status": "alive",
            "checks": {
                "api": "ok",
                "service": "alive"
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
                "status": "healthy",
                "service": f"{self.service_name}-database",
                "timestamp": self.response.timestamp,
                "database": {
                    "status": "healthy",
                    "connection": "ok",
                    "last_check": self.response.timestamp
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
        from ...data.database.dynamodb_connection import dynamodb_manager
        health_ok = dynamodb_manager.health_check()
        return health_ok
    except Exception as e:
        logger.warning(
            action=LogActions.ERROR,
            message=f"Database health check failed: {e}"
        )
        return False