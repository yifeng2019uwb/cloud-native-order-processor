"""
Shared Package - Cross-Cutting Infrastructure

This package contains cross-cutting infrastructure that is shared
across all services in the CNOP system.
"""

from .logging import BaseLogger
from .health import (
    HealthChecker,
    HealthCheckResponse,
    create_health_checker,
    get_database_health
)

__all__ = [
    # Logging
    "BaseLogger",

    # Health
    "HealthChecker",
    "HealthCheckResponse",
    "create_health_checker",
    "get_database_health"
]
