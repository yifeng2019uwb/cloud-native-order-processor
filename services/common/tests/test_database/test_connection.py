# Fix for services/tests/test_database/test_connection.py
# Update the async mock tests to properly handle coroutines and new _build_database_url method

import pytest
import os
from unittest.mock import patch, AsyncMock, MagicMock
import asyncpg

from database.connection import DatabaseManager, get_db, db_manager


class TestDatabaseManager:
    """Test cases for DatabaseManager class."""

    def test_init_calls_build_database_url(self):
        """Test DatabaseManager initialization calls _build_database_url."""
        with patch.object(
            DatabaseManager, "_build_database_url", return_value="test://url"
        ) as mock_build:
            db_mgr = DatabaseManager()
            mock_build.assert_called_once()
            assert db_mgr.database_url == "test://url"
            assert db_mgr.pool is None

    def test_build_database_url_with_complete_url(self):
        """Test _build_database_url with complete DATABASE_URL."""
        complete_url = "postgresql://user:pass@terraform-host:5432/db"
        with patch.dict(os.environ, {"DATABASE_URL": complete_url}):
            db_mgr = DatabaseManager()
            assert db_mgr.database_url == complete_url

    def test_build_database_url_with_components(self):
        """Test _build_database_url with individual components."""
        env_vars = {
            "DB_HOST": "terraform-rds-endpoint.amazonaws.com",
            "DB_PORT": "5432",
            "DB_NAME": "orderprocessor",
            "DB_USER": "orderuser",
            "DB_PASSWORD": "terraform-generated-password",
        }
        with patch.dict(os.environ, env_vars, clear=True):
            db_mgr = DatabaseManager()
            expected_url = "postgresql://orderuser:terraform-generated-password@terraform-rds-endpoint.amazonaws.com:5432/orderprocessor"
            assert db_mgr.database_url == expected_url

    def test_build_database_url_missing_db_host_uses_fallback(self):
        """Test _build_database_url falls back to localhost when DB_HOST missing."""
        env_vars = {"DB_PASSWORD": "test-password"}
        with patch.dict(os.environ, env_vars, clear=True):
            with patch("database.connection.logger") as mock_logger:
                db_mgr = DatabaseManager()
                expected_url = (
                    "postgresql://orderuser:test-password@localhost:5432/orderprocessor"
                )
                assert db_mgr.database_url == expected_url
                mock_logger.warning.assert_called_once()

    def test_build_database_url_missing_password_uses_fallback(self):
        """Test _build_database_url falls back when DB_PASSWORD missing."""
        env_vars = {"DB_HOST": "terraform-host"}
        with patch.dict(os.environ, env_vars, clear=True):
            with patch("database.connection.logger") as mock_logger:
                db_mgr = DatabaseManager()
                expected_url = "postgresql://orderuser:ChangeThisPassword123!@localhost:5432/orderprocessor"
                assert db_mgr.database_url == expected_url
                mock_logger.warning.assert_called_once()

    def test_build_database_url_default_values(self):
        """Test _build_database_url with default values for optional components."""
        env_vars = {
            "DB_HOST": "terraform-host",
            "DB_PASSWORD": "terraform-password",
            # DB_PORT, DB_NAME, DB_USER should use defaults
        }
        with patch.dict(os.environ, env_vars, clear=True):
            db_mgr = DatabaseManager()
            expected_url = "postgresql://orderuser:terraform-password@terraform-host:5432/orderprocessor"
            assert db_mgr.database_url == expected_url

    def test_build_database_url_custom_port_and_db_name(self):
        """Test _build_database_url with custom port and database name."""
        env_vars = {
            "DB_HOST": "terraform-host",
            "DB_PORT": "5433",
            "DB_NAME": "custom_db",
            "DB_USER": "custom_user",
            "DB_PASSWORD": "terraform-password",
        }
        with patch.dict(os.environ, env_vars, clear=True):
            db_mgr = DatabaseManager()
            expected_url = "postgresql://custom_user:terraform-password@terraform-host:5433/custom_db"
            assert db_mgr.database_url == expected_url

    def test_build_database_url_precedence(self):
        """Test that DATABASE_URL takes precedence over individual components."""
        complete_url = "postgresql://complete:url@complete-host:5432/complete_db"
        env_vars = {
            "DATABASE_URL": complete_url,
            "DB_HOST": "component-host",
            "DB_PASSWORD": "component-password",
        }
        with patch.dict(os.environ, env_vars, clear=True):
            db_mgr = DatabaseManager()
            assert db_mgr.database_url == complete_url

    @pytest.mark.asyncio
    async def test_init_pool_success(self):
        """Test successful pool initialization."""
        with patch.object(
            DatabaseManager, "_build_database_url", return_value="test://url"
        ):
            db_mgr = DatabaseManager()
            mock_pool = AsyncMock()

            # Create a proper async mock that can be awaited
            async def mock_create_pool(*args, **kwargs):
                return mock_pool

            with patch("asyncpg.create_pool", side_effect=mock_create_pool):
                await db_mgr.init_pool()
                assert db_mgr.pool == mock_pool

    @pytest.mark.asyncio
    async def test_init_pool_already_initialized(self):
        """Test that pool initialization is skipped if pool already exists."""
        with patch.object(
            DatabaseManager, "_build_database_url", return_value="test://url"
        ):
            db_mgr = DatabaseManager()
            existing_pool = AsyncMock()
            db_mgr.pool = existing_pool

            with patch("asyncpg.create_pool") as mock_create_pool:
                await db_mgr.init_pool()

                mock_create_pool.assert_not_called()
                assert db_mgr.pool == existing_pool

    @pytest.mark.asyncio
    async def test_close_pool_success(self):
        """Test successful pool closure."""
        with patch.object(
            DatabaseManager, "_build_database_url", return_value="test://url"
        ):
            db_mgr = DatabaseManager()
            mock_pool = AsyncMock()
            db_mgr.pool = mock_pool

            await db_mgr.close_pool()

            mock_pool.close.assert_called_once()
            assert db_mgr.pool is None

    @pytest.mark.asyncio
    async def test_close_pool_no_pool(self):
        """Test pool closure when no pool exists."""
        with patch.object(
            DatabaseManager, "_build_database_url", return_value="test://url"
        ):
            db_mgr = DatabaseManager()
            db_mgr.pool = None

            # Should not raise an exception
            await db_mgr.close_pool()
            assert db_mgr.pool is None

    @pytest.mark.asyncio
    async def test_get_connection_success(self):
        """Test successful connection acquisition."""
        with patch.object(
            DatabaseManager, "_build_database_url", return_value="test://url"
        ):
            db_mgr = DatabaseManager()
            mock_connection = AsyncMock()

            # Create a proper async context manager mock
            class MockAcquireContext:
                async def __aenter__(self):
                    return mock_connection

                async def __aexit__(self, exc_type, exc_val, exc_tb):
                    return None

            # Create a mock pool with acquire method that returns context manager directly
            mock_pool = MagicMock()
            mock_pool.acquire.return_value = MockAcquireContext()

            db_mgr.pool = mock_pool

            async with db_mgr.get_connection() as conn:
                assert conn == mock_connection

    @pytest.mark.asyncio
    async def test_get_connection_initializes_pool(self):
        """Test that get_connection initializes pool if not exists."""
        with patch.object(
            DatabaseManager, "_build_database_url", return_value="test://url"
        ):
            db_mgr = DatabaseManager()
            mock_connection = AsyncMock()

            # Create a proper async context manager mock
            class MockAcquireContext:
                async def __aenter__(self):
                    return mock_connection

                async def __aexit__(self, exc_type, exc_val, exc_tb):
                    return None

            # Create a mock pool with acquire method that returns context manager directly
            mock_pool = MagicMock()
            mock_pool.acquire.return_value = MockAcquireContext()

            # Mock init_pool to set the pool
            async def mock_init_pool():
                db_mgr.pool = mock_pool

            with patch.object(db_mgr, "init_pool", side_effect=mock_init_pool):
                async with db_mgr.get_connection() as conn:
                    assert conn == mock_connection

    @pytest.mark.asyncio
    async def test_get_connection_error_handling(self):
        """Test error handling in get_connection."""
        with patch.object(
            DatabaseManager, "_build_database_url", return_value="test://url"
        ):
            db_mgr = DatabaseManager()

            with patch.object(
                db_mgr, "init_pool", side_effect=Exception("Connection failed")
            ):
                with pytest.raises(Exception, match="Connection failed"):
                    async with db_mgr.get_connection():
                        pass


class TestGetDbDependency:
    """Test cases for get_db dependency function."""

    @pytest.mark.asyncio
    async def test_get_db_yields_connection(self):
        """Test that get_db yields a database connection."""
        mock_connection = AsyncMock()
        mock_context_manager = AsyncMock()
        mock_context_manager.__aenter__ = AsyncMock(return_value=mock_connection)
        mock_context_manager.__aexit__ = AsyncMock(return_value=None)

        with patch.object(
            db_manager, "get_connection", return_value=mock_context_manager
        ):
            async for conn in get_db():
                assert conn == mock_connection
                break

    @pytest.mark.asyncio
    async def test_get_db_handles_context_manager(self):
        """Test that get_db properly handles the async context manager."""
        mock_connection = AsyncMock()
        mock_context_manager = AsyncMock()
        mock_context_manager.__aenter__ = AsyncMock(return_value=mock_connection)
        mock_context_manager.__aexit__ = AsyncMock(return_value=None)

        with patch.object(
            db_manager, "get_connection", return_value=mock_context_manager
        ):
            connections = []
            async for conn in get_db():
                connections.append(conn)
                break

            assert len(connections) == 1
            assert connections[0] == mock_connection
            mock_context_manager.__aenter__.assert_called_once()


class TestGlobalDatabaseManager:
    """Test cases for the global database manager instance."""

    def test_global_db_manager_exists(self):
        """Test that global db_manager instance exists."""
        assert db_manager is not None
        assert isinstance(db_manager, DatabaseManager)

    def test_global_db_manager_singleton_behavior(self):
        """Test that importing db_manager returns the same instance."""
        from database.connection import db_manager as db_manager2

        assert db_manager is db_manager2


class TestDatabaseUrlBuildingIntegration:
    """Integration tests for database URL building with different scenarios."""

    def test_terraform_production_scenario(self):
        """Test typical Terraform production environment variables."""
        terraform_env = {
            "DB_HOST": "order-processor-dev-postgres.abc123.us-west-2.rds.amazonaws.com",
            "DB_NAME": "orderprocessor",
            "DB_USER": "orderuser",
            "DB_PASSWORD": "terraform-managed-password-123",
            "DB_PORT": "5432",
        }

        with patch.dict(os.environ, terraform_env, clear=True):
            db_mgr = DatabaseManager()
            expected_url = "postgresql://orderuser:terraform-managed-password-123@order-processor-dev-postgres.abc123.us-west-2.rds.amazonaws.com:5432/orderprocessor"
            assert db_mgr.database_url == expected_url

    def test_kubernetes_secret_scenario(self):
        """Test Kubernetes deployment with DATABASE_URL from secret."""
        k8s_env = {
            "DATABASE_URL": "postgresql://orderuser:k8s-secret-password@terraform-rds-endpoint:5432/orderprocessor"
        }

        with patch.dict(os.environ, k8s_env, clear=True):
            db_mgr = DatabaseManager()
            assert db_mgr.database_url == k8s_env["DATABASE_URL"]

    def test_local_development_scenario(self):
        """Test local development with minimal environment variables."""
        local_env = {"DB_PASSWORD": "local-dev-password"}

        with patch.dict(os.environ, local_env, clear=True):
            with patch("database.connection.logger") as mock_logger:
                db_mgr = DatabaseManager()
                expected_url = "postgresql://orderuser:local-dev-password@localhost:5432/orderprocessor"
                assert db_mgr.database_url == expected_url
                # Should log warning about using localhost
                mock_logger.warning.assert_called_once()

    def test_environment_variable_edge_cases(self):
        """Test edge cases in environment variable handling."""
        # Empty string values should be treated as missing
        edge_case_env = {
            "DATABASE_URL": "",
            "DB_HOST": "",
            "DB_PASSWORD": "valid-password",
        }

        with patch.dict(os.environ, edge_case_env, clear=True):
            with patch("database.connection.logger") as mock_logger:
                db_mgr = DatabaseManager()
                # Should fall back to localhost since DB_HOST is empty
                expected_url = "postgresql://orderuser:valid-password@localhost:5432/orderprocessor"
                assert db_mgr.database_url == expected_url
                mock_logger.warning.assert_called_once()

    def test_url_building_with_special_characters(self):
        """Test URL building with special characters in password."""
        special_char_env = {"DB_HOST": "terraform-host", "DB_PASSWORD": "p@ssw0rd!#$%"}

        with patch.dict(os.environ, special_char_env, clear=True):
            db_mgr = DatabaseManager()
            expected_url = (
                "postgresql://orderuser:p@ssw0rd!#$%@terraform-host:5432/orderprocessor"
            )
            assert db_mgr.database_url == expected_url
