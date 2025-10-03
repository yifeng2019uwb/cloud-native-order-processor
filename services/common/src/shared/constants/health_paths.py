"""
Health API paths constants for all services.

This module provides standardized health check endpoint paths
that should be used consistently across all microservices.
"""

from enum import Enum


class HealthPaths(str, Enum):
    """Standardized health check endpoint paths for all services."""

    # Basic health check - lightweight liveness probe
    HEALTH = "/health"

    # Readiness check - service ready to receive traffic
    HEALTH_READY = "/health/ready"

    # Liveness check - service is alive and responding
    HEALTH_LIVE = "/health/live"

    # Metrics endpoint - Prometheus metrics
    METRICS = "/metrics"

    # Internal metrics endpoint (if different from public metrics)
    INTERNAL_METRICS = "/internal/metrics"
