#!/usr/bin/env python3
"""
Redis connection manager for microservices.

Provides centralized Redis connection management with connection pooling,
retry logic, and health monitoring for all services.
"""

import os
from contextlib import contextmanager
from typing import Any, Dict, Optional

import redis

from ...shared.logging import BaseLogger, LogAction, LoggerName
from .redis_config import get_redis_config, get_redis_connection_params
from .database_constants import EnvironmentVariables, DefaultValues

logger = BaseLogger(LoggerName.CACHE, log_to_file=True)

class RedisConnectionManager:
    """Manages Redis connections with proper error handling and pooling"""

    def __init__(self):
        self._pool: Optional[redis.ConnectionPool] = None
        self._client: Optional[redis.Redis] = None
        self._config = get_redis_config()
        self._is_connected = False

    def _create_pool(self) -> redis.ConnectionPool:
        """Create Redis connection pool"""
        config = get_redis_connection_params()

        # Simple pool configuration
        max_connections = int(os.getenv(EnvironmentVariables.REDIS_MAX_CONNECTIONS, str(DefaultValues.DEFAULT_REDIS_MAX_CONNECTIONS)))

        return redis.ConnectionPool(
            host=config.host,
            port=config.port,
            db=config.db,
            password=config.password,
            decode_responses=config.decode_responses,
            socket_connect_timeout=config.socket_connect_timeout,
            socket_timeout=config.socket_timeout,
            retry_on_timeout=config.retry_on_timeout,
            health_check_interval=config.health_check_interval,
            max_connections=max_connections
        )

    def get_client(self) -> redis.Redis:
        """Get Redis client with connection pooling"""
        if self._client is None:
            if self._pool is None:
                self._pool = self._create_pool()

            self._client = redis.Redis(connection_pool=self._pool)
            logger.info(
                action=LogAction.CACHE_OPERATION,
                message=f"Created Redis client for {self._config.host}:{self._config.port}"
            )

        return self._client

    def test_connection(self) -> bool:
        """Test Redis connection"""
        try:
            client = self.get_client()
            client.ping()
            self._is_connected = True
            logger.info(
                action=LogAction.HEALTH_CHECK,
                message="Redis connection test successful"
            )
            return True
        except (redis.ConnectionError, redis.TimeoutError, redis.RedisError) as e:
            self._is_connected = False
            logger.error(
                action=LogAction.ERROR,
                message=f"Redis connection test failed: {e}"
            )
            return False

    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        return self._is_connected and self.test_connection()

    @contextmanager
    def get_connection(self):
        """Context manager for Redis operations with error handling"""
        client = self.get_client()
        try:
            yield client
        except (redis.ConnectionError, redis.TimeoutError) as e:
            logger.error(
                action=LogAction.ERROR,
                message=f"Redis connection error: {e}"
            )
            self._is_connected = False
            raise
        except redis.RedisError as e:
            logger.error(
                action=LogAction.ERROR,
                message=f"Redis operation error: {e}"
            )
            raise

    def close(self):
        """Close Redis connections"""
        if self._client:
            self._client.close()
            self._client = None

        if self._pool:
            self._pool.disconnect()
            self._pool = None

        self._is_connected = False
        logger.info(
            action=LogAction.CACHE_OPERATION,
            message="Redis connections closed"
        )

# Global connection manager instance
_redis_manager: Optional[RedisConnectionManager] = None

def get_redis_manager() -> RedisConnectionManager:
    """Get global Redis connection manager"""
    global _redis_manager
    if _redis_manager is None:
        _redis_manager = RedisConnectionManager()
    return _redis_manager

def get_redis_client() -> redis.Redis:
    """Get Redis client from global manager"""
    return get_redis_manager().get_client()

def test_redis_connection() -> bool:
    """Test Redis connection using global manager"""
    return get_redis_manager().test_connection()

def close_redis_connections():
    """Close all Redis connections"""
    global _redis_manager
    if _redis_manager:
        _redis_manager.close()
        _redis_manager = None
