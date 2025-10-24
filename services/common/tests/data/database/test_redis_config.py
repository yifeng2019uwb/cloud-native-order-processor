"""
Unit tests for Redis configuration management
"""

from unittest.mock import Mock, patch

import pytest

from src.data.database.redis_config import (RedisConfig, get_redis_config,
                                            get_redis_connection_params,
                                            get_redis_namespace, get_redis_url,
                                            is_local_kubernetes)
from src.data.database.database_constants import is_production


class TestRedisConfig:
    """Test RedisConfig dataclass"""

    def test_redis_config_default_values(self):
        """Test RedisConfig with default values"""
        config = RedisConfig(host="localhost", port=6379)

        assert config.host == "localhost"
        assert config.port == 6379
        assert config.db == 0
        assert config.password is None
        assert config.ssl is False
        assert config.ssl_cert_reqs is None
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
            ssl=True,
            ssl_cert_reqs="required",
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
        assert config.ssl is True
        assert config.ssl_cert_reqs == "required"
        assert config.decode_responses is False
        assert config.socket_connect_timeout == 15
        assert config.socket_timeout == 20
        assert config.retry_on_timeout is False
        assert config.health_check_interval == 60


class TestGetRedisConfig:
    """Test get_redis_config function"""

    @patch('src.data.database.redis_config.os.getenv')
    def test_get_redis_config_dev_environment(self, mock_getenv):
        """Test Redis configuration for dev environment"""
        # Mock environment variables for dev
        mock_getenv.side_effect = lambda key, default=None: {
            "ENVIRONMENT": "dev",
            "REDIS_HOST": "redis.local",
            "REDIS_PORT": "6380",
            "REDIS_DB": "1",
            "REDIS_PASSWORD": "devpass"
        }.get(key, default)

        config = get_redis_config()

        assert config.host == "redis.local"
        assert config.port == 6380
        assert config.db == 1
        assert config.password == "devpass"
        assert config.ssl is False
        assert config.ssl_cert_reqs is None
        assert config.socket_connect_timeout == 5
        assert config.socket_timeout == 5

    @patch('src.data.database.redis_config.os.getenv')
    def test_get_redis_config_prod_environment(self, mock_getenv):
        """Test Redis configuration for prod environment"""
        # Mock environment variables for prod
        mock_getenv.side_effect = lambda key, default=None: {
            "ENVIRONMENT": "prod",
            "REDIS_HOST": "redis.prod",
            "REDIS_PORT": "6379",
            "REDIS_DB": "0",
            "REDIS_PASSWORD": "prodpass"
        }.get(key, default)

        config = get_redis_config()

        assert config.host == "redis.prod"
        assert config.port == 6379
        assert config.db == 0
        assert config.password == "prodpass"
        assert config.ssl is True
        assert config.ssl_cert_reqs == "required"
        assert config.socket_connect_timeout == 10
        assert config.socket_timeout == 10

    @patch('src.data.database.redis_config.os.getenv')
    def test_get_redis_config_prod_with_aws_endpoint(self, mock_getenv):
        """Test Redis configuration for prod environment with AWS endpoint"""
        # Mock environment variables for prod with AWS endpoint
        mock_getenv.side_effect = lambda key, default=None: {
            "ENVIRONMENT": "prod",
            "REDIS_HOST": "redis.prod",
            "REDIS_PORT": "6379",
            "REDIS_DB": "0",
            "REDIS_PASSWORD": "prodpass",
            "REDIS_ENDPOINT": "redis-cluster.abc123.cache.amazonaws.com"
        }.get(key, default)

        config = get_redis_config()

        # Should use AWS endpoint instead of default host
        assert config.host == "redis-cluster.abc123.cache.amazonaws.com"
        assert config.port == 6379
        assert config.db == 0
        assert config.password == "prodpass"
        assert config.ssl is True
        assert config.ssl_cert_reqs == "required"
        assert config.socket_connect_timeout == 10
        assert config.socket_timeout == 10

    @patch('src.data.database.redis_config.os.getenv')
    def test_get_redis_config_default_values(self,  mock_getenv):
        """Test Redis configuration with default values when env vars are not set"""
        # Mock environment variables with minimal values
        mock_getenv.side_effect = lambda key, default=None: {
            "ENVIRONMENT": "dev"
        }.get(key, default)

        config = get_redis_config()

        assert config.host == "redis.order-processor.svc.cluster.local"
        assert config.port == 6379
        assert config.db == 0
        assert config.password is None
        assert config.ssl is False
        assert config.ssl_cert_reqs is None
        assert config.socket_connect_timeout == 5
        assert config.socket_timeout == 5
        assert config.retry_on_timeout is True
        assert config.health_check_interval == 30

    @patch('src.data.database.redis_config.os.getenv')
    def test_get_redis_config_case_insensitive_environment(self, mock_getenv):
        """Test Redis configuration with case-insensitive environment detection"""
        # Mock environment variables with uppercase environment
        mock_getenv.side_effect = lambda key, default=None: {
            "ENVIRONMENT": "PROD",
            "REDIS_HOST": "redis.prod",
            "REDIS_PORT": "6379",
            "REDIS_DB": "0"
        }.get(key, default)

        config = get_redis_config()

        # Should treat "PROD" as production environment
        assert config.ssl is True
        assert config.ssl_cert_reqs == "required"
        assert config.socket_connect_timeout == 10
        assert config.socket_timeout == 10


class TestGetRedisURL:
    """Test get_redis_url function"""

    @patch('src.data.database.redis_config.get_redis_config')
    def test_get_redis_url_no_ssl_no_password(self, mock_get_config):
        """Test Redis URL generation without SSL and password"""
        mock_config = Mock()
        mock_config.ssl = False
        mock_config.password = None
        mock_config.host = "localhost"
        mock_config.port = 6379
        mock_config.db = 0
        mock_get_config.return_value = mock_config

        url = get_redis_url()

        assert url == "redis://localhost:6379/0"

    @patch('src.data.database.redis_config.get_redis_config')
    def test_get_redis_url_with_ssl_no_password(self, mock_get_config):
        """Test Redis URL generation with SSL but no password"""
        mock_config = Mock()
        mock_config.ssl = True
        mock_config.password = None
        mock_config.host = "redis.example.com"
        mock_config.port = 6380
        mock_config.db = 1
        mock_get_config.return_value = mock_config

        url = get_redis_url()

        assert url == "rediss://redis.example.com:6380/1"

    @patch('src.data.database.redis_config.get_redis_config')
    def test_get_redis_url_with_ssl_and_password(self, mock_get_config):
        """Test Redis URL generation with SSL and password"""
        mock_config = Mock()
        mock_config.ssl = True
        mock_config.password = "secret123"
        mock_config.host = "redis.secure.com"
        mock_config.port = 6379
        mock_config.db = 0
        mock_get_config.return_value = mock_config

        url = get_redis_url()

        assert url == "rediss://:secret123@redis.secure.com:6379/0"

    @patch('src.data.database.redis_config.get_redis_config')
    def test_get_redis_url_no_ssl_with_password(self, mock_get_config):
        """Test Redis URL generation without SSL but with password"""
        mock_config = Mock()
        mock_config.ssl = False
        mock_config.password = "devpass"
        mock_config.host = "localhost"
        mock_config.port = 6380
        mock_config.db = 1
        mock_get_config.return_value = mock_config

        url = get_redis_url()

        assert url == "redis://:devpass@localhost:6380/1"


class TestGetRedisConnectionParams:
    """Test get_redis_connection_params function"""

    @patch('src.data.database.redis_config.get_redis_config')
    def test_get_redis_connection_params_basic(self, mock_get_config):
        """Test Redis connection parameters without SSL and password"""
        mock_config = Mock()
        mock_config.host = "localhost"
        mock_config.port = 6379
        mock_config.db = 0
        mock_config.password = None
        mock_config.ssl = False
        mock_config.ssl_cert_reqs = None
        mock_config.decode_responses = True
        mock_config.socket_connect_timeout = 5
        mock_config.socket_timeout = 5
        mock_config.retry_on_timeout = True
        mock_config.health_check_interval = 30
        mock_get_config.return_value = mock_config

        params = get_redis_connection_params()

        expected_params = {
            "host": "localhost",
            "port": 6379,
            "db": 0,
            "decode_responses": True,
            "socket_connect_timeout": 5,
            "socket_timeout": 5,
            "retry_on_timeout": True,
            "health_check_interval": 30
        }
        assert params == expected_params

    @patch('src.data.database.redis_config.get_redis_config')
    def test_get_redis_connection_params_with_password(self, mock_get_config):
        """Test Redis connection parameters with password"""
        mock_config = Mock()
        mock_config.host = "localhost"
        mock_config.port = 6379
        mock_config.db = 0
        mock_config.password = "secret123"
        mock_config.ssl = False
        mock_config.ssl_cert_reqs = None
        mock_config.decode_responses = True
        mock_config.socket_connect_timeout = 5
        mock_config.socket_timeout = 5
        mock_config.retry_on_timeout = True
        mock_config.health_check_interval = 30
        mock_get_config.return_value = mock_config

        params = get_redis_connection_params()

        expected_params = {
            "host": "localhost",
            "port": 6379,
            "db": 0,
            "password": "secret123",
            "decode_responses": True,
            "socket_connect_timeout": 5,
            "socket_timeout": 5,
            "retry_on_timeout": True,
            "health_check_interval": 30
        }
        assert params == expected_params

    @patch('src.data.database.redis_config.get_redis_config')
    def test_get_redis_connection_params_with_ssl(self, mock_get_config):
        """Test Redis connection parameters with SSL"""
        mock_config = Mock()
        mock_config.host = "redis.secure.com"
        mock_config.port = 6380
        mock_config.db = 1
        mock_config.password = None
        mock_config.ssl = True
        mock_config.ssl_cert_reqs = "required"
        mock_config.decode_responses = False
        mock_config.socket_connect_timeout = 10
        mock_config.socket_timeout = 15
        mock_config.retry_on_timeout = False
        mock_config.health_check_interval = 60
        mock_get_config.return_value = mock_config

        params = get_redis_connection_params()

        expected_params = {
            "host": "redis.secure.com",
            "port": 6380,
            "db": 1,
            "decode_responses": False,
            "socket_connect_timeout": 10,
            "socket_timeout": 15,
            "retry_on_timeout": False,
            "health_check_interval": 60,
            "ssl": True,
            "ssl_cert_reqs": "required"
        }
        assert params == expected_params

    @patch('src.data.database.redis_config.get_redis_config')
    def test_get_redis_connection_params_with_ssl_and_password(self, mock_get_config):
        """Test Redis connection parameters with SSL and password"""
        mock_config = Mock()
        mock_config.host = "redis.secure.com"
        mock_config.port = 6380
        mock_config.db = 1
        mock_config.password = "securepass"
        mock_config.ssl = True
        mock_config.ssl_cert_reqs = "required"
        mock_config.decode_responses = True
        mock_config.socket_connect_timeout = 10
        mock_config.socket_timeout = 10
        mock_config.retry_on_timeout = True
        mock_config.health_check_interval = 30
        mock_get_config.return_value = mock_config

        params = get_redis_connection_params()

        expected_params = {
            "host": "redis.secure.com",
            "port": 6380,
            "db": 1,
            "password": "securepass",
            "decode_responses": True,
            "socket_connect_timeout": 10,
            "socket_timeout": 10,
            "retry_on_timeout": True,
            "health_check_interval": 30,
            "ssl": True,
            "ssl_cert_reqs": "required"
        }
        assert params == expected_params


class TestEnvironmentHelpers:
    """Test environment detection helper functions"""

    @patch('src.data.database.redis_config.os.getenv')
    def test_is_production_true(self, mock_getenv):
        """Test is_production when environment is prod"""
        mock_getenv.return_value = "prod"

        result = is_production()

        assert result is True
        mock_getenv.assert_called_once_with("ENVIRONMENT", "dev")

    @patch('src.data.database.redis_config.os.getenv')
    def test_is_production_false(self, mock_getenv):
        """Test is_production when environment is not prod"""
        mock_getenv.return_value = "dev"

        result = is_production()

        assert result is False
        mock_getenv.assert_called_once_with("ENVIRONMENT", "dev")

    @patch('src.data.database.redis_config.os.getenv')
    def test_is_production_case_insensitive(self, mock_getenv):
        """Test is_production with case-insensitive environment detection"""
        mock_getenv.return_value = "PROD"

        result = is_production()

        assert result is True
        mock_getenv.assert_called_once_with("ENVIRONMENT", "dev")

    @patch('src.data.database.redis_config.os.getenv')
    def test_is_production_default_value(self, mock_getenv):
        """Test is_production when environment variable is not set"""
        # Mock getenv to return the default value "dev" when ENVIRONMENT is not set
        mock_getenv.side_effect = lambda key, default=None: default if key == "ENVIRONMENT" else None

        result = is_production()

        assert result is False
        mock_getenv.assert_called_once_with("ENVIRONMENT", "dev")

    @patch('src.data.database.redis_config.os.getenv')
    def test_is_local_kubernetes_true(self, mock_getenv):
        """Test is_local_kubernetes when environment is dev"""
        mock_getenv.return_value = "dev"

        result = is_local_kubernetes()

        assert result is True
        mock_getenv.assert_called_once_with("ENVIRONMENT", "dev")

    @patch('src.data.database.redis_config.os.getenv')
    def test_is_local_kubernetes_false(self, mock_getenv):
        """Test is_local_kubernetes when environment is not dev"""
        mock_getenv.return_value = "prod"

        result = is_local_kubernetes()

        assert result is False
        mock_getenv.assert_called_once_with("ENVIRONMENT", "dev")

    @patch('src.data.database.redis_config.os.getenv')
    def test_is_local_kubernetes_case_insensitive(self, mock_getenv):
        """Test is_local_kubernetes with case-insensitive environment detection"""
        mock_getenv.return_value = "DEV"

        result = is_local_kubernetes()

        assert result is True
        mock_getenv.assert_called_once_with("ENVIRONMENT", "dev")

    @patch('src.data.database.redis_config.os.getenv')
    def test_is_local_kubernetes_default_value(self, mock_getenv):
        """Test is_local_kubernetes when environment variable is not set"""
        # Mock getenv to return the default value "dev" when ENVIRONMENT is not set
        mock_getenv.side_effect = lambda key, default=None: default if key == "ENVIRONMENT" else None

        result = is_local_kubernetes()

        assert result is True
        mock_getenv.assert_called_once_with("ENVIRONMENT", "dev")

    @patch('src.data.database.redis_config.os.getenv')
    def test_get_redis_namespace_dev(self, mock_getenv):
        """Test get_redis_namespace for dev environment"""
        mock_getenv.return_value = "dev"

        namespace = get_redis_namespace()

        assert namespace == "order-processor:dev"
        mock_getenv.assert_called_once_with("ENVIRONMENT", "dev")

    @patch('src.data.database.redis_config.os.getenv')
    def test_get_redis_namespace_prod(self, mock_getenv):
        """Test get_redis_namespace for prod environment"""
        mock_getenv.return_value = "prod"

        namespace = get_redis_namespace()

        assert namespace == "order-processor:prod"
        mock_getenv.assert_called_once_with("ENVIRONMENT", "dev")

    @patch('src.data.database.redis_config.os.getenv')
    def test_get_redis_namespace_case_insensitive(self, mock_getenv):
        """Test get_redis_namespace with case-insensitive environment detection"""
        mock_getenv.return_value = "STAGING"

        namespace = get_redis_namespace()

        assert namespace == "order-processor:staging"
        mock_getenv.assert_called_once_with("ENVIRONMENT", "dev")

    @patch('src.data.database.redis_config.os.getenv')
    def test_get_redis_namespace_default_value(self, mock_getenv):
        """Test get_redis_namespace when environment variable is not set"""
        # Mock getenv to return the default value "dev" when ENVIRONMENT is not set
        mock_getenv.side_effect = lambda key, default=None: default if key == "ENVIRONMENT" else None

        namespace = get_redis_namespace()

        assert namespace == "order-processor:dev"
        mock_getenv.assert_called_once_with("ENVIRONMENT", "dev")
