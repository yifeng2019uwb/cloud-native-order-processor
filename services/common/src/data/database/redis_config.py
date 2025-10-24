#!/usr/bin/env python3
"""
Redis configuration and connection management.

Provides centralized Redis configuration and connection management
for all microservices.
"""

import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

import redis

from ...shared.logging import BaseLogger, LogAction, LoggerName
from .database_constants import (
    build_redis_config,
    build_redis_pool_params,
    get_environment,
    is_development,
    get_redis_namespace,
    RedisConfig as RedisConfigConstants,
)

logger = BaseLogger(LoggerName.CACHE, log_to_file=True)

@dataclass
class RedisConfig:
    """Redis configuration for different environments"""
    host: str
    port: int
    db: int = 0
    password: Optional[str] = None
    ssl: bool = False
    ssl_cert_reqs: Optional[str] = None
    decode_responses: bool = True
    socket_connect_timeout: int = 5
    socket_timeout: int = 5
    retry_on_timeout: bool = True
    health_check_interval: int = 30

def get_redis_config() -> RedisConfig:
    """
    Get Redis configuration based on environment
    Supports both local K8s and AWS environments
    """
    environment = get_environment()
    config = build_redis_config()

    logger.info(
        action=LogAction.CACHE_OPERATION,
        message=f"Redis configuration for {environment}: {config['host']}:{config['port']}"
    )
    return RedisConfig(**config)

def get_redis_url() -> str:
    """
    Get Redis URL for connection string format
    Useful for libraries that expect URL format
    """
    config = get_redis_config()

    # Build URL components
    scheme = RedisConfigConstants.REDISS_SCHEME if config.ssl else RedisConfigConstants.REDIS_SCHEME
    auth = f":{config.password}@" if config.password else ""

    return f"{scheme}://{auth}{config.host}:{config.port}/{config.db}"

def get_redis_connection_params() -> Dict[str, Any]:
    """
    Get Redis connection parameters as dictionary
    Useful for redis-py library
    """
    config = get_redis_config()

    params = {
        RedisConfigConstants.HOST_KEY: config.host,
        RedisConfigConstants.PORT_KEY: config.port,
        RedisConfigConstants.DB_KEY: config.db,
        RedisConfigConstants.DECODE_RESPONSES_KEY: config.decode_responses,
        RedisConfigConstants.SOCKET_CONNECT_TIMEOUT_KEY: config.socket_connect_timeout,
        RedisConfigConstants.SOCKET_TIMEOUT_KEY: config.socket_timeout,
        RedisConfigConstants.RETRY_ON_TIMEOUT_KEY: config.retry_on_timeout,
        RedisConfigConstants.HEALTH_CHECK_INTERVAL_KEY: config.health_check_interval,
    }

    # Add optional parameters
    if config.password:
        params[RedisConfigConstants.PASSWORD_KEY] = config.password

    if config.ssl:
        params[RedisConfigConstants.SSL_KEY] = config.ssl
        params[RedisConfigConstants.SSL_CERT_REQS_KEY] = config.ssl_cert_reqs

    return params

# Environment detection helpers
def is_local_kubernetes() -> bool:
    """Check if running in local K8s environment"""
    return is_development()