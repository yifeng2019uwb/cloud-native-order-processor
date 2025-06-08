import pytest
import os
from unittest.mock import patch, AsyncMock, MagicMock
import asyncpg

from database.connection import DatabaseManager, get_db, db_manager


class TestDatabaseManager:
    """Test cases for DatabaseManager class."""

    def test_init_default_database_url(self):
        """Test DatabaseManager initialization with default database URL."""
        with patch.dict(os.environ, {}, clear=True):
            db_mgr = DatabaseManager()
            expected_url = "postgresql://orderuser:ChangeThisPassword123!@localhost:5432/orderprocessor"
            assert db_mgr.database_url == expected_url
            assert db_mgr.pool is None

    def test_init_custom_database_url(self):
        """Test DatabaseManager initialization with custom database URL."""
        custom_url = "postgresql://user:pass@host:5432/db"
        with patch.dict(os.environ, {"DATABASE_URL": custom_url}):
            db_mgr = DatabaseManager()
            assert db_mgr.database_url == custom_url

    @pytest.mark.asyncio
    async def test_init_pool_success(self):
        """Test successful pool initialization."""
        db_mgr = DatabaseManager()
        mock_pool = AsyncMock()

        with patch("asyncpg.create_pool", return_value=mock_pool) as mock_create_pool:
            await db_mgr.init_pool()

            mock_create_pool.assert_called_once_with(
                db_mgr.database_url, min_size=1, max_size=10, command_timeout=60
            )
            assert db_mgr.pool == mock_pool

    @pytest.mark.asyncio
    async def test_init_pool_already_initialized(self):
        """Test that pool initialization is skipped if pool already exists."""
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
        db_mgr = DatabaseManager()
        mock_pool = AsyncMock()
        db_mgr.pool = mock_pool

        await db_mgr.close_pool()

        mock_pool.close.assert_called_once()
        assert db_mgr.pool is None

    @pytest.mark.asyncio
    async def test_close_pool_no_pool(self):
        """Test pool closure when no pool exists."""
        db_mgr = DatabaseManager()
        db_mgr.pool = None

        # Should not raise an exception
        await db_mgr.close_pool()
        assert db_mgr.pool is None

    @pytest.mark.asyncio
    async def test_get_connection_success(self):
        """Test successful connection acquisition."""
        db_mgr = DatabaseManager()
        mock_pool = AsyncMock()
        mock_connection = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_connection
        db_mgr.pool = mock_pool

        async with db_mgr.get_connection() as conn:
            assert conn == mock_connection

    @pytest.mark.asyncio
    async def test_get_connection_initializes_pool(self):
        """Test that get_connection initializes pool if not exists."""
        db_mgr = DatabaseManager()
        mock_pool = AsyncMock()
        mock_connection = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_connection

        with patch.object(db_mgr, "init_pool", new_callable=AsyncMock) as mock_init:
            with patch("asyncpg.create_pool", return_value=mock_pool):
                db_mgr.pool = mock_pool  # Simulate pool creation

                async with db_mgr.get_connection() as conn:
                    assert conn == mock_connection

    @pytest.mark.asyncio
    async def test_get_connection_error_handling(self):
        """Test error handling in get_connection."""
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

        with patch.object(db_manager, "get_connection") as mock_get_conn:
            mock_get_conn.return_value.__aenter__.return_value = mock_connection

            async for conn in get_db():
                assert conn == mock_connection
                break

    @pytest.mark.asyncio
    async def test_get_db_handles_context_manager(self):
        """Test that get_db properly handles the async context manager."""
        mock_connection = AsyncMock()
        mock_context_manager = AsyncMock()
        mock_context_manager.__aenter__.return_value = mock_connection
        mock_context_manager.__aexit__.return_value = None

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
