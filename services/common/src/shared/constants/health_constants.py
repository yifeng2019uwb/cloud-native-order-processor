#!/usr/bin/env python3
"""
Health check constants.

Centralizes all health check related constants to avoid hardcoded values.
"""


class HealthCheckConstants:
    """Health check related constants"""

    # Health status values
    STATUS_HEALTHY = "healthy"
    STATUS_UNHEALTHY = "unhealthy"
    STATUS_OK = "OK"
    STATUS_FAILED = "FAILED"

    # Health check field names
    STATUS = "status"
    TIMESTAMP = "timestamp"
    LAST_CHECK = "last_check"
    CHECK_INTERVAL_SECONDS = "check_interval_seconds"
    HOST = "host"
    PORT = "port"
    SSL_ENABLED = "ssl_enabled"
    CONNECTION_POOL_SIZE = "connection_pool_size"
    UNKNOWN = "unknown"

    # Default values
    DEFAULT_CHECK_INTERVAL = 30

    # Health check response values
    SERVICE = "service"
    VERSION = "version"
    ENVIRONMENT = "environment"
    CHECKS = "checks"
    API = "api"
    DATABASE = "database"
    CONNECTION = "connection"

    # Health check status values
    RUNNING = "running"
    READY = "ready"
    ALIVE = "alive"
    OK = "ok"

    # Environment defaults
    DEFAULT_ENVIRONMENT = "development"
