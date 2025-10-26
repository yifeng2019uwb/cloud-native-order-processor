#!/usr/bin/env python3
"""
Redis health check for services
Provides health status and connection monitoring
"""

from typing import Optional

from ...data.database.redis_connection import test_redis_connection
from ...shared.logging import BaseLogger, LogAction, LoggerName

logger = BaseLogger(LoggerName.CACHE, log_to_file=True)

class RedisHealthChecker:
    """Simplified Redis health checker - only checks if healthy or not"""

    def is_healthy(self) -> bool:
        """Check if Redis is healthy"""
        try:
            status = test_redis_connection()

            if status:
                logger.info(
                    action=LogAction.HEALTH_CHECK,
                    message="Redis health check: OK"
                )
            else:
                logger.warning(
                    action=LogAction.ERROR,
                    message="Redis health check: FAILED"
                )

            return status

        except Exception as e:
            logger.error(
                action=LogAction.ERROR,
                message=f"Redis health check error: {e}"
            )
            return False

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