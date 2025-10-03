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

from ...shared.logging import BaseLogger, LogActions, Loggers
from .redis_config import (RedisConfig, get_redis_config,
                           get_redis_connection_params)

logger = BaseLogger(Loggers.CACHE, log_to_file=True)

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
            "max_connections": int(os.getenv("REDIS_MAX_CONNECTIONS", "10")),
            "retry_on_timeout": params.get("retry_on_timeout", True),
            "socket_connect_timeout": params.get("socket_connect_timeout", 5),
            "socket_timeout": params.get("socket_timeout", 5),
            "health_check_interval": params.get("health_check_interval", 30),
        }

        # Create pool based on SSL configuration
        if params.get("ssl"):
            return redis.ConnectionPool.from_url(
                f"rediss://{params['host']}:{params['port']}/{params['db']}",
                **pool_params,
                ssl_cert_reqs=params.get("ssl_cert_reqs", "required")
            )
        else:
            return redis.ConnectionPool(
                host=params["host"],
                port=params["port"],
                db=params["db"],
                password=params.get("password"),
                decode_responses=params.get("decode_responses", True),
                **pool_params
            )

    def get_client(self) -> redis.Redis:
        """Get Redis client with connection pooling"""
        if self._client is None:
            if self._pool is None:
                self._pool = self._create_pool()

            self._client = redis.Redis(connection_pool=self._pool)
            logger.info(
                action=LogActions.CACHE_OPERATION,
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
                action=LogActions.HEALTH_CHECK,
                message="Redis connection test successful"
            )
            return True
        except (redis.ConnectionError, redis.TimeoutError, redis.RedisError) as e:
            self._is_connected = False
            logger.error(
                action=LogActions.ERROR,
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
                action=LogActions.ERROR,
                message=f"Redis connection error: {e}"
            )
            self._is_connected = False
            raise
        except redis.RedisError as e:
            logger.error(
                action=LogActions.ERROR,
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
            action=LogActions.CACHE_OPERATION,
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

# Utility functions for common Redis operations
def redis_set(key: str, value: str, expire: Optional[int] = None) -> bool:
    """Set Redis key with optional expiration"""
    try:
        with get_redis_manager().get_connection() as client:
            if expire:
                return client.setex(key, expire, value)
            else:
                return client.set(key, value)
    except redis.RedisError as e:
        logger.error(
            action=LogActions.ERROR,
            message=f"Failed to set Redis key {key}: {e}"
        )
        return False

def redis_get(key: str) -> Optional[str]:
    """Get Redis key value"""
    try:
        with get_redis_manager().get_connection() as client:
            return client.get(key)
    except redis.RedisError as e:
        logger.error(
            action=LogActions.ERROR,
            message=f"Failed to get Redis key {key}: {e}"
        )
        return None

def redis_delete(key: str) -> bool:
    """Delete Redis key"""
    try:
        with get_redis_manager().get_connection() as client:
            return bool(client.delete(key))
    except redis.RedisError as e:
        logger.error(
            action=LogActions.ERROR,
            message=f"Failed to delete Redis key {key}: {e}"
        )
        return False

def redis_exists(key: str) -> bool:
    """Check if Redis key exists"""
    try:
        with get_redis_manager().get_connection() as client:
            return bool(client.exists(key))
    except redis.RedisError as e:
        logger.error(
            action=LogActions.ERROR,
            message=f"Failed to check Redis key {key}: {e}"
        )
        return False