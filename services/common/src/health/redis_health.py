#!/usr/bin/env python3
"""
Redis health check for services
Provides health status and connection monitoring
"""

import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime

from ..database.redis_connection import get_redis_manager, test_redis_connection

logger = logging.getLogger(__name__)

class RedisHealthChecker:
    """Redis health checker for service monitoring"""

    def __init__(self):
        self._last_check: Optional[datetime] = None
        self._last_status: Optional[bool] = None
        self._check_interval = 30  # seconds

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
                logger.debug("Redis health check: OK")
            else:
                logger.warning("Redis health check: FAILED")

            return status

        except Exception as e:
            logger.error(f"Redis health check error: {e}")
            self._last_status = False
            self._last_check = now
            return False

    def get_health_status(self) -> Dict[str, Any]:
        """Get detailed health status"""
        is_healthy = self.is_healthy()

        status = {
            "status": "healthy" if is_healthy else "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "last_check": self._last_check.isoformat() if self._last_check else None,
            "check_interval_seconds": self._check_interval,
        }

        # Add connection details if available
        try:
            manager = get_redis_manager()
            config = manager._config
            status.update({
                "host": config.host,
                "port": config.port,
                "ssl_enabled": config.ssl,
                "connection_pool_size": getattr(manager._pool, 'max_connections', 'unknown') if manager._pool else 'unknown'
            })
        except Exception as e:
            logger.warning(f"Could not get Redis connection details: {e}")

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