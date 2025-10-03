"""
Shared Package - Cross-Cutting Infrastructure

This package contains cross-cutting infrastructure that is shared
across all services in the CNOP system.
"""

from .health import HealthChecker, HealthCheckResponse, create_health_checker

__all__ = [
    # Health
    "HealthChecker",
    "HealthCheckResponse",
    "create_health_checker"
]
