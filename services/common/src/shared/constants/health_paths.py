"""
Health API paths constants for all services.

This module provides standardized health check endpoint paths
that should be used consistently across all microservices.
"""

from enum import Enum


class HealthPaths(str, Enum):
    """Standardized health check endpoint paths for all services."""

    # Single health check endpoint for Docker and Kubernetes
    HEALTH = "/health"

    # Metrics endpoint - Prometheus metrics
    METRICS = "/metrics"

    # Internal metrics endpoint (if different from public metrics)
    INTERNAL_METRICS = "/internal/metrics"
