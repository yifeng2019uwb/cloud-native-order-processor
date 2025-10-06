#!/usr/bin/env python3
"""
Redis health check for services
Provides health status and connection monitoring
"""

import time
from datetime import datetime
from typing import Any, Dict, Optional

from ...data.database.redis_connection import (get_redis_manager,
                                               test_redis_connection)
from ...shared.constants.health_constants import HealthCheckConstants
from ...shared.logging import BaseLogger, LogActions, Loggers

logger = BaseLogger(Loggers.CACHE, log_to_file=True)

class RedisHealthChecker:
    """Redis health checker for service monitoring"""

    def __init__(self):
        self._last_check: Optional[datetime] = None
        self._last_status: Optional[bool] = None
        self._check_interval = HealthCheckConstants.DEFAULT_CHECK_INTERVAL  # seconds

    def is_healthy(self) -> bool:
        """Check if Redis is healthy"""
        now = datetime.now()

        # Use cached result if recent
        if (self._last_check and
            (now - self._last_check).total_seconds() < self._check_interval):
            return self._last_status

        # Perform health check
        try:
            status = test_redis_connection()
            self._last_status = status
            self._last_check = now

            if status:
                logger.info(
                    action=LogActions.HEALTH_CHECK,
                    message=f"Redis health check: {HealthCheckConstants.STATUS_OK}"
                )
            else:
                logger.warning(
                    action=LogActions.ERROR,
                    message=f"Redis health check: {HealthCheckConstants.STATUS_FAILED}"
                )

            return status

        except Exception as e:
            logger.error(
                action=LogActions.ERROR,
                message=f"Redis health check error: {e}"
            )
            self._last_status = False
            self._last_check = now
            return False

    def get_health_status(self) -> Dict[str, Any]:
        """Get detailed health status"""
        is_healthy = self.is_healthy()

        status = {
            HealthCheckConstants.STATUS: HealthCheckConstants.STATUS_HEALTHY if is_healthy else HealthCheckConstants.STATUS_UNHEALTHY,
            HealthCheckConstants.TIMESTAMP: datetime.now().isoformat(),
            HealthCheckConstants.LAST_CHECK: self._last_check.isoformat() if self._last_check else None,
            HealthCheckConstants.CHECK_INTERVAL_SECONDS: self._check_interval,
        }

        # Add connection details if available
        try:
            manager = get_redis_manager()
            config = manager._config
            status.update({
                HealthCheckConstants.HOST: config.host,
                HealthCheckConstants.PORT: config.port,
                HealthCheckConstants.SSL_ENABLED: config.ssl,
                HealthCheckConstants.CONNECTION_POOL_SIZE: getattr(manager._pool, 'max_connections', HealthCheckConstants.UNKNOWN) if manager._pool else HealthCheckConstants.UNKNOWN
            })
        except Exception as e:
            logger.warning(
                action=LogActions.ERROR,
                message=f"Could not get Redis connection details: {e}"
            )

        return status

# Global health checker instance
_redis_health_checker: Optional[RedisHealthChecker] = None

def get_redis_health_checker() -> RedisHealthChecker:
    """Get global Redis health checker"""
    global _redis_health_checker
    if _redis_health_checker is None:
        _redis_health_checker = RedisHealthChecker()
    return _redis_health_checker

def check_redis_health() -> bool:
    """Quick Redis health check"""
    return get_redis_health_checker().is_healthy()

def get_redis_health_status() -> Dict[str, Any]:
    """Get detailed Redis health status"""
    return get_redis_health_checker().get_health_status()