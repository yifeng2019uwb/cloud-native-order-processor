"""
Unit tests for Redis configuration management
"""

from unittest.mock import patch

import pytest

from src.data.database.redis_config import RedisConfig, get_redis_config, get_redis_connection_params, get_redis_url
from tests.utils.dependency_constants import REDIS_CONFIG_OS_GETENV

# =============================================================================
# LOCAL TEST VARIABLES - Avoid hardcoded values in tests
# =============================================================================

# Test values
TEST_REDIS_HOST_LOCAL = "localhost"
TEST_REDIS_HOST_DEFAULT = "redis.order-processor.svc.cluster.local"
TEST_REDIS_PORT_DEFAULT = "6379"
TEST_REDIS_DB_DEFAULT = "0"
TEST_REDIS_PASSWORD_TEST = "testpass"


class TestRedisConfig:
    """Test RedisConfig dataclass"""

    def test_redis_config_default_values(self):
        """Test RedisConfig with default values"""
        config = RedisConfig(host="localhost", port=6379)

        assert config.host == "localhost"
        assert config.port == 6379
        assert config.db == 0
        assert config.password is None
        assert config.decode_responses is True
        assert config.socket_connect_timeout == 5
        assert config.socket_timeout == 5
        assert config.retry_on_timeout is True
        assert config.health_check_interval == 30

    def test_redis_config_custom_values(self):
        """Test RedisConfig with custom values"""
        config = RedisConfig(
            host="redis.example.com",
            port=6380,
            db=1,
            password="secret123",
            decode_responses=False,
            socket_connect_timeout=15,
            socket_timeout=20,
            retry_on_timeout=False,
            health_check_interval=60
        )

        assert config.host == "redis.example.com"
        assert config.port == 6380
        assert config.db == 1
        assert config.password == "secret123"
        assert config.decode_responses is False
        assert config.socket_connect_timeout == 15
        assert config.socket_timeout == 20
        assert config.retry_on_timeout is False
        assert config.health_check_interval == 60


class TestGetRedisConfig:
    """Test get_redis_config function"""

    @patch(REDIS_CONFIG_OS_GETENV)
    def test_get_redis_config_with_custom_values(self, mock_getenv):
        """Test Redis configuration with custom environment variables"""
        mock_getenv.side_effect = lambda key, default=None: {
            "REDIS_HOST": TEST_REDIS_HOST_LOCAL,
            "REDIS_PORT": TEST_REDIS_PORT_DEFAULT,
            "REDIS_DB": TEST_REDIS_DB_DEFAULT,
            "REDIS_PASSWORD": TEST_REDIS_PASSWORD_TEST
        }.get(key, default)

        config = get_redis_config()

        assert config.host == TEST_REDIS_HOST_LOCAL
        assert config.port == int(TEST_REDIS_PORT_DEFAULT)
        assert config.db == int(TEST_REDIS_DB_DEFAULT)
        assert config.password == TEST_REDIS_PASSWORD_TEST

    @patch(REDIS_CONFIG_OS_GETENV)
    def test_get_redis_config_default_values(self, mock_getenv):
        """Test Redis configuration with default values when env vars are not set"""
        # Mock getenv to return None for Redis environment variables, but use defaults
        mock_getenv.side_effect = lambda key, default=None: default

        config = get_redis_config()

        assert config.host == TEST_REDIS_HOST_DEFAULT
        assert config.port == int(TEST_REDIS_PORT_DEFAULT)
        assert config.db == int(TEST_REDIS_DB_DEFAULT)
        assert config.password is None


class TestGetRedisURL:
    """Test get_redis_url function"""

    @patch(REDIS_CONFIG_OS_GETENV)
    def test_get_redis_url_basic(self, mock_getenv):
        """Test Redis URL generation"""
        # Mock environment to return test values
        mock_getenv.side_effect = lambda key, default=None: {
            "REDIS_HOST": TEST_REDIS_HOST_LOCAL,
            "REDIS_PORT": TEST_REDIS_PORT_DEFAULT,
            "REDIS_DB": TEST_REDIS_DB_DEFAULT,
            "REDIS_PASSWORD": None
        }.get(key, default)

        url = get_redis_url()
        assert url == f"redis://{TEST_REDIS_HOST_LOCAL}:{TEST_REDIS_PORT_DEFAULT}/{TEST_REDIS_DB_DEFAULT}"

    @patch(REDIS_CONFIG_OS_GETENV)
    def test_get_redis_url_with_password(self, mock_getenv):
        """Test Redis URL generation with password"""
        # Mock environment to return test values with password
        mock_getenv.side_effect = lambda key, default=None: {
            "REDIS_HOST": TEST_REDIS_HOST_LOCAL,
            "REDIS_PORT": TEST_REDIS_PORT_DEFAULT,
            "REDIS_DB": TEST_REDIS_DB_DEFAULT,
            "REDIS_PASSWORD": TEST_REDIS_PASSWORD_TEST
        }.get(key, default)

        url = get_redis_url()
        assert url == f"redis://:{TEST_REDIS_PASSWORD_TEST}@{TEST_REDIS_HOST_LOCAL}:{TEST_REDIS_PORT_DEFAULT}/{TEST_REDIS_DB_DEFAULT}"


class TestGetRedisConnectionParams:
    """Test get_redis_connection_params function"""

    def test_get_redis_connection_params_returns_config_object(self):
        """Test that get_redis_connection_params returns RedisConfig object"""
        params = get_redis_connection_params()

        # Should return a RedisConfig object, not a dictionary
        assert isinstance(params, RedisConfig)
        assert hasattr(params, 'host')
        assert hasattr(params, 'port')
        assert hasattr(params, 'db')
