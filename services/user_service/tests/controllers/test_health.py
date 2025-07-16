"""
Unit tests for src/controllers/health.py - Health check controller
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException, status
from datetime import datetime, timezone
import os

from controllers.health import (
    basic_health_check,
    readiness_check,
    database_health_check,
    check_database_health,
    detailed_database_check,
    router
)


class TestHealthFunctions:
    """Test individual health functions"""

    @pytest.mark.asyncio
    async def test_basic_health_check_success(self):
        """Test successful basic health check"""
        result = await basic_health_check()

        assert result["status"] == "healthy"
        assert result["service"] == "user-auth-service"
        assert result["version"] == "1.0.0"
        assert "timestamp" in result
        assert "environment" in result
        assert "checks" in result
        assert result["checks"]["api"] == "ok"
        assert result["checks"]["service"] == "running"

    @patch('controllers.health.os.getenv')
    @pytest.mark.asyncio
    async def test_basic_health_check_with_jwt_secret(self, mock_getenv):
        """Test basic health check when JWT_SECRET is set"""
        mock_getenv.return_value = "test-secret"

        result = await basic_health_check()

        assert result["checks"]["jwt"] == "ok"

    @patch('controllers.health.os.getenv')
    @pytest.mark.asyncio
    async def test_basic_health_check_without_jwt_secret(self, mock_getenv):
        """Test basic health check when JWT_SECRET is not set"""
        mock_getenv.return_value = None

        result = await basic_health_check()

        assert result["checks"]["jwt"] == "using_default"

    @patch('controllers.health.check_database_health')
    @pytest.mark.asyncio
    async def test_readiness_check_success(self, mock_db_health):
        """Test successful readiness check"""
        mock_db_health.return_value = True

        result = await readiness_check()

        assert result["status"] == "ready"
        assert result["service"] == "user-auth-service"
        assert result["version"] == "1.0.0"
        assert "timestamp" in result
        assert result["checks"]["api"] == "ok"
        assert result["checks"]["database"] == "ok"
        assert result["checks"]["service"] == "ready"

    @patch('controllers.health.check_database_health')
    @pytest.mark.asyncio
    async def test_readiness_check_database_unhealthy(self, mock_db_health):
        """Test readiness check when database is unhealthy"""
        mock_db_health.return_value = False

        with pytest.raises(HTTPException) as exc_info:
            await readiness_check()

        assert exc_info.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert "Database not ready" in str(exc_info.value.detail)

    @patch('controllers.health.check_database_health')
    @pytest.mark.asyncio
    async def test_readiness_check_exception(self, mock_db_health):
        """Test readiness check when exception occurs"""
        mock_db_health.side_effect = Exception("Database connection failed")

        with pytest.raises(HTTPException) as exc_info:
            await readiness_check()

        assert exc_info.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert "Service not ready" in str(exc_info.value.detail)

    @patch('controllers.health.detailed_database_check')
    @pytest.mark.asyncio
    async def test_database_health_check_success(self, mock_db_check):
        """Test successful database health check"""
        mock_db_check.return_value = {
            "status": "healthy",
            "connection": "ok",
            "operations": {"user_query": "ok"},
            "statistics": {"sample_users_found": 5},
            "tables": {"users_table": "accessible"}
        }

        result = await database_health_check()

        assert result["status"] == "healthy"
        assert result["service"] == "user-auth-service-database"
        assert "timestamp" in result
        assert "database" in result
        assert result["database"]["status"] == "healthy"

    @patch('controllers.health.detailed_database_check')
    @pytest.mark.asyncio
    async def test_database_health_check_unhealthy(self, mock_db_check):
        """Test database health check when database is unhealthy"""
        mock_db_check.return_value = {
            "status": "unhealthy",
            "connection": "failed",
            "error": "Connection timeout"
        }

        with pytest.raises(HTTPException) as exc_info:
            await database_health_check()

        assert exc_info.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert "Database unhealthy" in str(exc_info.value.detail)

    @patch('controllers.health.detailed_database_check')
    @pytest.mark.asyncio
    async def test_database_health_check_exception(self, mock_db_check):
        """Test database health check when exception occurs"""
        mock_db_check.side_effect = Exception("Database check failed")

        with pytest.raises(HTTPException) as exc_info:
            await database_health_check()

        assert exc_info.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert "Database health check failed" in str(exc_info.value.detail)

    @patch('controllers.health.dynamodb_manager')
    @pytest.mark.asyncio
    async def test_check_database_health_success(self, mock_dynamodb_manager):
        """Test successful database health check helper"""
        mock_dynamodb_manager.health_check = AsyncMock(return_value=True)

        result = await check_database_health()

        assert result is True
        mock_dynamodb_manager.health_check.assert_called_once()

    @patch('controllers.health.dynamodb_manager')
    @pytest.mark.asyncio
    async def test_check_database_health_failure(self, mock_dynamodb_manager):
        """Test database health check helper when database is unhealthy"""
        mock_dynamodb_manager.health_check.return_value = False

        result = await check_database_health()

        assert result is False

    @patch('controllers.health.dynamodb_manager')
    @pytest.mark.asyncio
    async def test_check_database_health_exception(self, mock_dynamodb_manager):
        """Test database health check helper when exception occurs"""
        mock_dynamodb_manager.health_check.side_effect = Exception("Connection failed")

        result = await check_database_health()

        assert result is False

    @patch('controllers.health.UserDAO')
    @patch('controllers.health.dynamodb_manager')
    @pytest.mark.asyncio
    async def test_detailed_database_check_success(self, mock_dynamodb_manager, mock_user_dao_class):
        """Test successful detailed database check"""
        # Setup mocks
        mock_connection = Mock()
        mock_dynamodb_manager.get_connection.return_value.__aenter__.return_value = mock_connection

        mock_user_dao = Mock()
        mock_user_dao_class.return_value = mock_user_dao

        # Mock successful table scan
        mock_response = {"Count": 5}
        mock_user_dao.db.users_table.scan.return_value = mock_response

        result = await detailed_database_check()

        assert result["status"] == "healthy"
        assert result["connection"] == "ok"
        assert result["operations"]["user_query"] == "ok"
        assert result["statistics"]["sample_users_found"] == 5
        assert result["tables"]["users_table"] == "accessible"
        assert "last_check" in result

    @patch('controllers.health.UserDAO')
    @patch('controllers.health.dynamodb_manager')
    @pytest.mark.asyncio
    async def test_detailed_database_check_scan_failure(self, mock_dynamodb_manager, mock_user_dao_class):
        """Test detailed database check when table scan fails"""
        # Setup mocks
        mock_connection = Mock()
        mock_dynamodb_manager.get_connection.return_value.__aenter__.return_value = mock_connection

        mock_user_dao = Mock()
        mock_user_dao_class.return_value = mock_user_dao

        # Mock failed table scan
        mock_user_dao.db.users_table.scan.side_effect = Exception("Table scan failed")

        result = await detailed_database_check()

        assert result["status"] == "healthy"
        assert result["connection"] == "ok"
        assert result["operations"]["user_query"] == "failed"
        assert result["statistics"]["sample_users_found"] == 0
        assert result["tables"]["users_table"] == "accessible"

    @patch('controllers.health.dynamodb_manager')
    @pytest.mark.asyncio
    async def test_detailed_database_check_connection_failure(self, mock_dynamodb_manager):
        """Test detailed database check when connection fails"""
        # Mock connection failure
        mock_dynamodb_manager.get_connection.side_effect = Exception("Connection failed")

        result = await detailed_database_check()

        assert result["status"] == "unhealthy"
        assert result["connection"] == "failed"
        assert "error" in result
        assert "last_check" in result


class TestHealthRouter:
    """Test the health router configuration"""

    def test_router_configuration(self):
        """Test that the router is properly configured"""
        assert "health" in router.tags

        # Check that routes are registered
        routes = [route.path for route in router.routes]
        expected_routes = ["/health", "/health/ready", "/health/db"]

        for expected_route in expected_routes:
            assert any(expected_route in route for route in routes)