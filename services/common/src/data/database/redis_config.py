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
from .database_constants import EnvironmentVariables, DefaultValues, RedisConfig as RedisConfigConstants

logger = BaseLogger(LoggerName.CACHE, log_to_file=True)

@dataclass
class RedisConfig:
    """Simplified Redis configuration"""
    host: str
    port: int
    db: int = DefaultValues.DEFAULT_REDIS_DB
    password: Optional[str] = None
    decode_responses: bool = True
    socket_connect_timeout: int = RedisConfigConstants.SOCKET_CONNECT_TIMEOUT
    socket_timeout: int = RedisConfigConstants.SOCKET_TIMEOUT
    retry_on_timeout: bool = RedisConfigConstants.RETRY_ON_TIMEOUT
    health_check_interval: int = RedisConfigConstants.HEALTH_CHECK_INTERVAL

def get_redis_config() -> RedisConfig:
    """
    Get simplified Redis configuration from environment variables
    """
    host = os.getenv(EnvironmentVariables.REDIS_HOST, DefaultValues.DEFAULT_REDIS_HOST)
    port_str = os.getenv(EnvironmentVariables.REDIS_PORT, str(DefaultValues.DEFAULT_REDIS_PORT))
    db_str = os.getenv(EnvironmentVariables.REDIS_DB, str(DefaultValues.DEFAULT_REDIS_DB))
    password = os.getenv(EnvironmentVariables.REDIS_PASSWORD)

    # Handle None values from mocked environment
    port = int(port_str) if port_str is not None else DefaultValues.DEFAULT_REDIS_PORT
    db = int(db_str) if db_str is not None else DefaultValues.DEFAULT_REDIS_DB

    logger.info(
        action=LogAction.CACHE_OPERATION,
        message=f"Redis configuration: {host}:{port}"
    )

    return RedisConfig(
        host=host,
        port=port,
        db=db,
        password=password
    )

def get_redis_url() -> str:
    """
    Get Redis URL for connection string format
    """
    config = get_redis_config()
    auth = f":{config.password}@" if config.password else ""
    return f"redis://{auth}{config.host}:{config.port}/{config.db}"

def get_redis_connection_params() -> RedisConfig:
    """
    Get Redis connection parameters as RedisConfig object
    """
    return get_redis_config()