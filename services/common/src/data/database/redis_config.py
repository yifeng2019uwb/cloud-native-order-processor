#!/usr/bin/env python3
"""
Redis configuration and connection management.

Provides centralized Redis configuration and connection management
for all microservices.
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
from ...shared.logging import BaseLogger, Loggers, LogActions
import redis

logger = BaseLogger(Loggers.CACHE, log_to_file=True)

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
    environment = os.getenv("ENVIRONMENT", "dev").lower()

    # Base configuration
    config = {
        "host": os.getenv("REDIS_HOST", "redis.order-processor.svc.cluster.local"),
        "port": int(os.getenv("REDIS_PORT", "6379")),
        "db": int(os.getenv("REDIS_DB", "0")),
        "password": os.getenv("REDIS_PASSWORD"),
        "decode_responses": True,
        "socket_connect_timeout": 5,
        "socket_timeout": 5,
        "retry_on_timeout": True,
        "health_check_interval": 30,
    }

    # Environment-specific overrides
    if environment == "prod":
        # AWS ElastiCache configuration
        config.update({
            "ssl": True,
            "ssl_cert_reqs": "required",
            "socket_connect_timeout": 10,
            "socket_timeout": 10,
        })

        # Use AWS ElastiCache endpoint if available
        aws_redis_endpoint = os.getenv("REDIS_ENDPOINT")
        if aws_redis_endpoint:
            config["host"] = aws_redis_endpoint

    else:
        # Local K8s configuration
        config.update({
            "ssl": False,
            "ssl_cert_reqs": None,
        })

    logger.info(
        action=LogActions.CACHE_OPERATION,
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
    scheme = "rediss" if config.ssl else "redis"
    auth = f":{config.password}@" if config.password else ""

    return f"{scheme}://{auth}{config.host}:{config.port}/{config.db}"

def get_redis_connection_params() -> Dict[str, Any]:
    """
    Get Redis connection parameters as dictionary
    Useful for redis-py library
    """
    config = get_redis_config()

    params = {
        "host": config.host,
        "port": config.port,
        "db": config.db,
        "decode_responses": config.decode_responses,
        "socket_connect_timeout": config.socket_connect_timeout,
        "socket_timeout": config.socket_timeout,
        "retry_on_timeout": config.retry_on_timeout,
        "health_check_interval": config.health_check_interval,
    }

    # Add optional parameters
    if config.password:
        params["password"] = config.password

    if config.ssl:
        params["ssl"] = config.ssl
        params["ssl_cert_reqs"] = config.ssl_cert_reqs

    return params

# Environment detection helpers
def is_production() -> bool:
    """Check if running in production environment"""
    return os.getenv("ENVIRONMENT", "dev").lower() == "prod"

def is_local_kubernetes() -> bool:
    """Check if running in local K8s environment"""
    return os.getenv("ENVIRONMENT", "dev").lower() == "dev"

def get_redis_namespace() -> str:
    """Get Redis namespace for key prefixing"""
    environment = os.getenv("ENVIRONMENT", "dev").lower()
    return f"order-processor:{environment}"