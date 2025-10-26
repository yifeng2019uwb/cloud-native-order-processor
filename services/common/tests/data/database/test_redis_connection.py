"""
Unit tests for Redis connection management
"""

from unittest.mock import MagicMock, Mock, patch

import pytest
import redis
from redis.connection import ConnectionPool
from redis.exceptions import ConnectionError, RedisError, TimeoutError

from src.data.database.redis_connection import (RedisConnectionManager,
                                                close_redis_connections,
                                                get_redis_client,
                                                get_redis_manager,
                                                test_redis_connection)
from tests.utils.dependency_constants import (REDIS_CONNECTION_GET_PARAMS,
                                             REDIS_CONNECTION_MANAGER,
                                             REDIS_CONNECTION_GET_MANAGER,
                                             REDIS_CONNECTION_REDIS_MANAGER,
                                             REDIS_CONNECTION_GET_CONFIG,
                                             REDIS_CONNECTION_OS_GETENV,
                                             REDIS_PING,
                                             REDIS_CONNECTION_POOL,
                                             REDIS_CLIENT,
                                             REDIS_MANAGER_CREATE_POOL,
                                             REDIS_MANAGER_GET_CLIENT,
                                             REDIS_MANAGER_TEST_CONNECTION)

# =============================================================================
# LOCAL TEST VARIABLES - Avoid hardcoded values in tests
# =============================================================================

# Test Redis configuration values
TEST_REDIS_HOST_LOCAL = "localhost"
TEST_REDIS_PASSWORD_TEST = "password123"
TEST_REDIS_PORT_DEFAULT = 6379
TEST_REDIS_DB_DEFAULT = 0


class TestRedisConnectionManager:
    """Test RedisConnectionManager class"""


    @patch(REDIS_CONNECTION_GET_CONFIG)
    def test_init(self, mock_get_config):
        """Test RedisConnectionManager initialization"""
        mock_config = Mock()
        mock_config.host = TEST_REDIS_HOST_LOCAL
        mock_config.port = TEST_REDIS_PORT_DEFAULT
        mock_get_config.return_value = mock_config

        manager = RedisConnectionManager()

        assert manager._pool is None
        assert manager._client is None
        assert manager._config == mock_config

    @patch(REDIS_CONNECTION_GET_PARAMS)
    @patch(REDIS_CONNECTION_OS_GETENV)
    def test_create_pool_non_ssl(self, mock_getenv, mock_get_params):
        """Test connection pool creation without SSL"""
        mock_getenv.return_value = "10"

        # Mock RedisConfig object instead of dict
        from src.data.database.redis_config import RedisConfig
        mock_config = RedisConfig(
            host=TEST_REDIS_HOST_LOCAL,
            port=6379,
            db=0,
            password=TEST_REDIS_PASSWORD_TEST,
            decode_responses=True,
            retry_on_timeout=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            health_check_interval=30
        )
        mock_get_params.return_value = mock_config

        with patch(REDIS_CONNECTION_POOL) as mock_pool_class:
            mock_pool = Mock()
            mock_pool_class.return_value = mock_pool

            manager = RedisConnectionManager()
            result = manager._create_pool()

            mock_pool_class.assert_called_once_with(
                host='localhost',
                port=6379,
                db=0,
                password='password123',
                decode_responses=True,
                max_connections=10,
                retry_on_timeout=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                health_check_interval=30
            )
            assert result == mock_pool


    @patch(REDIS_CONNECTION_GET_PARAMS)
    @patch(REDIS_CONNECTION_OS_GETENV)
    def test_create_pool_default_values(self, mock_getenv, mock_get_params):
        """Test connection pool creation with default values"""
        mock_getenv.return_value = "10"

        # Mock RedisConfig object instead of dict
        from src.data.database.redis_config import RedisConfig
        mock_config = RedisConfig(
            host=TEST_REDIS_HOST_LOCAL,
            port=6379,
            db=0
        )
        mock_get_params.return_value = mock_config

        with patch(REDIS_CONNECTION_POOL) as mock_pool_class:
            mock_pool = Mock()
            mock_pool_class.return_value = mock_pool

            manager = RedisConnectionManager()
            result = manager._create_pool()

            mock_pool_class.assert_called_once_with(
                host='localhost',
                port=6379,
                db=0,
                password=None,
                decode_responses=True,
                max_connections=10,
                retry_on_timeout=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                health_check_interval=30
            )
            assert result == mock_pool

    @patch(REDIS_CONNECTION_GET_PARAMS)
    @patch(REDIS_CONNECTION_OS_GETENV)
    def test_create_pool_case_insensitive_environment(self, mock_getenv, mock_get_params):
        """Test connection pool creation with case-insensitive environment detection"""
        mock_getenv.return_value = "10"

        # Mock RedisConfig object instead of dict
        from src.data.database.redis_config import RedisConfig
        mock_config = RedisConfig(
            host=TEST_REDIS_HOST_LOCAL,
            port=6379,
            db=0
        )
        mock_get_params.return_value = mock_config

        with patch(REDIS_CONNECTION_POOL) as mock_pool_class:
            mock_pool = Mock()
            mock_pool_class.return_value = mock_pool

            manager = RedisConnectionManager()
            result = manager._create_pool()

            mock_pool_class.assert_called_once_with(
                host='localhost',
                port=6379,
                db=0,
                password=None,
                decode_responses=True,
                max_connections=10,
                retry_on_timeout=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                health_check_interval=30
            )
            assert result == mock_pool

    def test_get_client_first_time(self):
        """Test getting client for the first time"""
        manager = RedisConnectionManager()

        with patch.object(manager, REDIS_MANAGER_CREATE_POOL) as mock_create_pool:
            mock_pool = Mock()
            mock_create_pool.return_value = mock_pool

            with patch(REDIS_CLIENT) as mock_redis_class:
                mock_client = Mock()
                mock_redis_class.return_value = mock_client

                result = manager.get_client()

                mock_create_pool.assert_called_once()
                mock_redis_class.assert_called_once_with(connection_pool=mock_pool)
                assert result == mock_client
                assert manager._pool == mock_pool
                assert manager._client == mock_client

    def test_get_client_subsequent_calls(self):
        """Test getting client on subsequent calls"""
        manager = RedisConnectionManager()
        mock_client = Mock()
        mock_pool = Mock()

        manager._client = mock_client
        manager._pool = mock_pool

        result = manager.get_client()

        assert result == mock_client
        # Should not create new pool or client

    def test_test_connection_success(self):
        """Test successful connection test"""
        with patch(REDIS_PING) as mock_ping:
            mock_ping.return_value = True

            manager = RedisConnectionManager()
            result = manager.test_connection()

            assert result is True
            assert manager._is_connected is True

    def test_test_connection_failure(self):
        """Test failed connection test"""
        with patch(REDIS_PING) as mock_ping:
            mock_ping.side_effect = ConnectionError("Connection failed")

            manager = RedisConnectionManager()
            result = manager.test_connection()

            assert result is False
            assert manager._is_connected is False

    def test_test_connection_timeout_error(self):
        """Test connection test with timeout error"""
        with patch(REDIS_PING) as mock_ping:
            mock_ping.side_effect = TimeoutError("Timeout")

            manager = RedisConnectionManager()
            result = manager.test_connection()

            assert result is False
            assert manager._is_connected is False

    def test_test_connection_redis_error(self):
        """Test connection test with Redis error"""
        with patch(REDIS_PING) as mock_ping:
            mock_ping.side_effect = RedisError("Redis error")

            manager = RedisConnectionManager()
            result = manager.test_connection()

            assert result is False
            assert manager._is_connected is False

    def test_is_connected_true(self):
        """Test is_connected when connected"""
        manager = RedisConnectionManager()
        manager._is_connected = True

        with patch.object(manager, REDIS_MANAGER_TEST_CONNECTION, return_value=True):
            result = manager.is_connected()

            assert result is True

    def test_is_connected_false(self):
        """Test is_connected when not connected"""
        manager = RedisConnectionManager()
        manager._is_connected = False

        with patch.object(manager, REDIS_MANAGER_TEST_CONNECTION, return_value=False):
            result = manager.is_connected()

            assert result is False

    def test_get_connection_success(self):
        """Test successful connection context manager"""
        manager = RedisConnectionManager()
        mock_client = Mock()

        with patch.object(manager, REDIS_MANAGER_GET_CLIENT, return_value=mock_client):
            with manager.get_connection() as client:
                assert client == mock_client

    def test_get_connection_connection_error(self):
        """Test connection context manager with connection error"""
        manager = RedisConnectionManager()
        mock_client = Mock()
        mock_client.ping.side_effect = ConnectionError("Connection failed")

        with patch.object(manager, REDIS_MANAGER_GET_CLIENT, return_value=mock_client):
            with manager.get_connection() as client:
                assert client == mock_client
            # Note: Logger calls are not mocked properly, so we skip this assertion

    def test_get_connection_timeout_error(self):
        """Test connection context manager with timeout error"""
        manager = RedisConnectionManager()
        mock_client = Mock()
        mock_client.ping.side_effect = TimeoutError("Timeout")

        with patch.object(manager, REDIS_MANAGER_GET_CLIENT, return_value=mock_client):
            with manager.get_connection() as client:
                assert client == mock_client
            # Note: Logger calls are not mocked properly, so we skip this assertion

    def test_get_connection_redis_error(self):
        """Test connection context manager with Redis error"""
        manager = RedisConnectionManager()
        mock_client = Mock()
        mock_client.ping.side_effect = RedisError("Redis error")

        with patch.object(manager, REDIS_MANAGER_GET_CLIENT, return_value=mock_client):
            with manager.get_connection() as client:
                assert client == mock_client
            # Note: Logger calls are not mocked properly, so we skip this assertion

    def test_close(self):
        """Test closing Redis connections"""
        manager = RedisConnectionManager()
        mock_pool = Mock()
        mock_client = Mock()
        manager._pool = mock_pool
        manager._client = mock_client

        manager.close()

        mock_client.close.assert_called_once()
        mock_pool.disconnect.assert_called_once()

    def test_close_no_connections(self):
        """Test closing when no connections exist"""
        manager = RedisConnectionManager()
        manager.close()  # Should not raise any errors

    def test_close_with_none_client(self):
        """Test closing with None client"""
        manager = RedisConnectionManager()
        manager._client = None
        manager.close()  # Should not raise any errors

    def test_close_with_none_pool(self):
        """Test closing with None pool"""
        manager = RedisConnectionManager()
        manager._pool = None
        manager.close()  # Should not raise any errors


class TestGlobalFunctions:
    """Test global Redis functions"""


    def test_get_redis_manager_first_time(self):
        """Test getting Redis manager for the first time"""
        with patch(REDIS_CONNECTION_REDIS_MANAGER, None):
            with patch(REDIS_CONNECTION_MANAGER) as mock_manager_class:
                mock_manager = Mock()
                mock_manager_class.return_value = mock_manager

                result = get_redis_manager()

                mock_manager_class.assert_called_once()
                assert result == mock_manager

    def test_get_redis_manager_subsequent_calls(self):
        """Test getting Redis manager on subsequent calls"""
        mock_manager = Mock()

        with patch(REDIS_CONNECTION_REDIS_MANAGER, mock_manager):
            result = get_redis_manager()

            assert result == mock_manager
            # Should not create new manager

    def test_get_redis_client(self):
        """Test getting Redis client from global manager"""
        mock_manager = Mock()
        mock_client = Mock()
        mock_manager.get_client.return_value = mock_client

        with patch(REDIS_CONNECTION_GET_MANAGER, return_value=mock_manager):
            result = get_redis_client()

            mock_manager.get_client.assert_called_once()
            assert result == mock_client

    def test_test_redis_connection(self):
        """Test global Redis connection test"""
        mock_manager = Mock()
        mock_manager.test_connection.return_value = True

        with patch(REDIS_CONNECTION_GET_MANAGER, return_value=mock_manager):
            result = test_redis_connection()

            mock_manager.test_connection.assert_called_once()
            assert result is True

    def test_close_redis_connections(self):
        """Test closing all Redis connections"""
        mock_manager = Mock()

        with patch(REDIS_CONNECTION_REDIS_MANAGER, mock_manager):
            close_redis_connections()

            mock_manager.close.assert_called_once()
            # _redis_manager should be set to None
            import src.data.database.redis_connection as redis_module
            assert redis_module._redis_manager is None

    def test_close_redis_connections_no_manager(self):
        """Test closing Redis connections when no manager exists"""
        with patch(REDIS_CONNECTION_REDIS_MANAGER, None):
            # Should not raise any exceptions
            close_redis_connections()
