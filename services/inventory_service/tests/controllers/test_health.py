import pytest
from unittest.mock import Mock, patch, AsyncMock

# Import exception classes for testing
from exceptions import InternalServerException
from common.exceptions import (
    DatabaseOperationException,
    ConfigurationException
)


def test_health_endpoint_function_import():
    # Test that the function can be imported
    from inventory_service.src.controllers.health import health_check
    assert callable(health_check)

def test_controllers_init_import():
    import inventory_service.src.controllers.__init__


class TestHealthControllerComprehensive:
    """Comprehensive tests for the health controller"""

    @pytest.mark.asyncio
    async def test_readiness_check_database_not_ready(self):
        """Test readiness check when database is not ready"""
        from controllers.health import readiness_check

        # Mock the database health check to return False
        with patch('controllers.health.check_database_health', return_value=False):
            with pytest.raises(InternalServerException) as exc_info:
                await readiness_check()

            error = exc_info.value
            # Check that the error message contains the operation context
            assert "readiness check failed" in str(error).lower()

    @pytest.mark.asyncio
    async def test_readiness_check_exception_handling(self):
        """Test readiness check exception handling"""
        from controllers.health import readiness_check

        # Mock the database health check to raise an exception
        with patch('controllers.health.check_database_health', side_effect=Exception("Health check failed")):
            with pytest.raises(InternalServerException) as exc_info:
                await readiness_check()

            error = exc_info.value
            # Check that the error message contains the operation context
            assert "readiness check failed" in str(error).lower()

    @pytest.mark.asyncio
    async def test_database_health_check_unhealthy_status(self):
        """Test database health check when status is unhealthy"""
        from controllers.health import database_health_check

        # Mock the detailed database check to return unhealthy status
        with patch('controllers.health.detailed_database_check', return_value={
            "status": "unhealthy",
            "error": "Connection timeout"
        }):
            with pytest.raises(InternalServerException) as exc_info:
                await database_health_check()

            error = exc_info.value
            # Check that the error message contains the operation context
            assert "database health check failed" in str(error).lower()

    @pytest.mark.asyncio
    async def test_database_health_check_exception_handling(self):
        """Test database health check exception handling"""
        from controllers.health import database_health_check

        # Mock the detailed database check to raise an exception
        with patch('controllers.health.detailed_database_check', side_effect=Exception("Health check failed")):
            with pytest.raises(InternalServerException) as exc_info:
                await database_health_check()

            error = exc_info.value
            # Check that the error message contains the operation context
            assert "database health check failed" in str(error).lower()

    @pytest.mark.asyncio
    async def test_readiness_check_with_common_package_exception(self):
        """Test readiness check with common package exception"""
        from controllers.health import readiness_check

        # Mock the database health check to raise a common package exception
        with patch('controllers.health.check_database_health', side_effect=DatabaseOperationException(
            "Connection failed", service="dynamodb"
        )):
            with pytest.raises(InternalServerException) as exc_info:
                await readiness_check()

            error = exc_info.value
            # Check that the error message contains the operation context
            assert "readiness check failed" in str(error).lower()

    @pytest.mark.asyncio
    async def test_database_health_check_with_common_package_exception(self):
        """Test database health check with common package exception"""
        from controllers.health import database_health_check

        # Mock the detailed database check to raise a common package exception
        with patch('controllers.health.detailed_database_check', side_effect=ConfigurationException(
            "Operation failed", operation="describe_table"
        )):
            with pytest.raises(InternalServerException) as exc_info:
                await database_health_check()

            error = exc_info.value
            # Check that the error message contains the operation context
            assert "database health check failed" in str(error).lower()

    @pytest.mark.asyncio
    async def test_health_controller_error_context(self):
        """Test that health controller provides proper error context"""
        from controllers.health import readiness_check

        # Mock the database health check to raise an exception
        with patch('controllers.health.check_database_health', side_effect=Exception("Test health error")):
            with pytest.raises(InternalServerException) as exc_info:
                await readiness_check()

            error = exc_info.value
            # Check that the error has proper context
            assert "readiness check failed" in str(error).lower()
            assert "Test health error" in str(error)

    @pytest.mark.asyncio
    async def test_health_controller_exception_flow(self):
        """Test the complete exception flow in health controller"""
        from controllers.health import database_health_check

        # Mock the detailed database check to raise a common package exception
        with patch('controllers.health.detailed_database_check', side_effect=ConfigurationException(
            "Operation failed", operation="describe_table", table="assets"
        )):
            with pytest.raises(InternalServerException) as exc_info:
                await database_health_check()

            error = exc_info.value
            # Verify the error is properly wrapped
            assert isinstance(error, InternalServerException)
            assert "database health check failed" in str(error).lower()

    @pytest.mark.asyncio
    async def test_health_controller_with_multiple_exceptions(self):
        """Test health controller handling multiple types of exceptions"""
        from controllers.health import readiness_check

        # Test with different exception types
        exceptions_to_test = [
            Exception("Generic exception"),
            ValueError("Value error"),
            RuntimeError("Runtime error"),
            DatabaseOperationException("Connection error", service="dynamodb"),
            ConfigurationException("Operation error", operation="scan")
        ]

        for exc in exceptions_to_test:
            with patch('controllers.health.check_database_health', side_effect=exc):
                with pytest.raises(InternalServerException) as exc_info:
                    await readiness_check()

                error = exc_info.value
                assert isinstance(error, InternalServerException)
                assert "readiness check failed" in str(error).lower()

    @pytest.mark.asyncio
    async def test_readiness_check_success(self):
        """Test readiness check when database is healthy"""
        from controllers.health import readiness_check

        # Mock the database health check to return True
        with patch('controllers.health.check_database_health', return_value=True):
            result = await readiness_check()

            assert result["status"] == "ready"
            assert result["service"] == "inventory-service"
            assert "timestamp" in result
            assert result["checks"]["database"] == "ok"

    @pytest.mark.asyncio
    async def test_database_health_check_success(self):
        """Test database health check when database is healthy"""
        from controllers.health import database_health_check

        # Mock the detailed database check to return healthy status
        with patch('controllers.health.detailed_database_check', return_value={
            "status": "healthy",
            "connection": "ok",
            "tables": ["assets"]
        }):
            result = await database_health_check()

            assert result["status"] == "healthy"
            assert result["service"] == "inventory-service-database"
            assert "timestamp" in result
            assert result["database"]["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_liveness_check(self):
        """Test liveness check endpoint"""
        from controllers.health import liveness_check

        result = await liveness_check()

        assert result["status"] == "alive"
        assert result["service"] == "inventory-service"
        assert "timestamp" in result
        assert result["checks"]["service"] == "alive"
        assert "database" not in result["checks"]  # Liveness check doesn't check database

    @pytest.mark.asyncio
    async def test_health_check_basic(self):
        """Test basic health check endpoint"""
        from controllers.health import health_check

        result = await health_check()

        assert result["status"] == "healthy"
        assert result["service"] == "inventory-service"
        assert "timestamp" in result