#!/usr/bin/env python3
"""
Redis connection manager for microservices.

Provides centralized Redis connection management with connection pooling,
retry logic, and health monitoring for all services.
"""

import os
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, Optional

import redis

from ...shared.logging import BaseLogger, LogAction, LoggerName
from .redis_config import (RedisConfig, get_redis_config,
                           get_redis_connection_params)
from .database_constants import (
    get_redis_max_connections,
    RedisConfig as RedisConfigConstants
)

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
        params = get_redis_connection_params()

        # Pool configuration
        pool_params = {
            RedisConfigConstants.MAX_CONNECTIONS_KEY: get_redis_max_connections(),
            RedisConfigConstants.RETRY_ON_TIMEOUT_KEY:
                params.get(RedisConfigConstants.RETRY_ON_TIMEOUT_KEY, RedisConfigConstants.RETRY_ON_TIMEOUT),
            RedisConfigConstants.SOCKET_CONNECT_TIMEOUT_KEY:
                params.get(RedisConfigConstants.SOCKET_CONNECT_TIMEOUT_KEY, RedisConfigConstants.SOCKET_CONNECT_TIMEOUT),
            RedisConfigConstants.SOCKET_TIMEOUT_KEY:
                params.get(RedisConfigConstants.SOCKET_TIMEOUT_KEY, RedisConfigConstants.SOCKET_TIMEOUT),
            RedisConfigConstants.HEALTH_CHECK_INTERVAL_KEY:
                params.get(RedisConfigConstants.HEALTH_CHECK_INTERVAL_KEY, RedisConfigConstants.HEALTH_CHECK_INTERVAL),
        }

        # Create pool based on SSL configuration
        if params.get(RedisConfigConstants.SSL_KEY):
            return redis.ConnectionPool.from_url(
                f"rediss://{params['host']}:{params['port']}/{params['db']}",
                **pool_params,
                ssl_cert_reqs=params.get(RedisConfigConstants.SSL_CERT_REQS_KEY, RedisConfigConstants.SSL_CERT_REQUIRED)
            )
        else:
            return redis.ConnectionPool(

                host=params[RedisConfigConstants.HOST_KEY],
                port=params[RedisConfigConstants.PORT_KEY],
                db=params[RedisConfigConstants.DB_KEY],
                password=params.get(RedisConfigConstants.PASSWORD_KEY),
                decode_responses=params.get(RedisConfigConstants.DECODE_RESPONSES_KEY, True),
                **pool_params
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
