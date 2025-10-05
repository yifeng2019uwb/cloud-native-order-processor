"""
Tests for Health Checks
"""

# Standard library imports
from unittest.mock import MagicMock, patch

# Third-party imports
import pytest
from fastapi import HTTPException

# Local imports
from src.shared.health import health_checks
from src.data.database import dynamodb_connection
from src.shared.health.health_checks import (HealthChecker,
                                             HealthCheckResponse,
                                             create_health_checker,
                                             get_database_health)


class TestHealthCheckResponse:
    """Test HealthCheckResponse class"""

    # Define patch paths as class constants
    PATH_GET_DB_HEALTH = f'{health_checks.__name__}.get_database_health'
    PATH_GET_MANAGER = f'{dynamodb_connection.__name__}.get_dynamodb_manager'

    def test_health_check_response_creation(self):
        """Test creating a HealthCheckResponse"""
        response = HealthCheckResponse(
            service_name="test-service",
            version="1.0.0",
            environment="test"
        )

        assert response.service_name == "test-service"
        assert response.version == "1.0.0"
        assert response.environment == "test"
        assert response.timestamp is not None

    def test_health_check_response_to_dict(self):
        """Test converting HealthCheckResponse to dictionary"""
        response = HealthCheckResponse("test-service")

        result = response.to_dict()
        assert result["status"] == "healthy"
        assert result["service"] == "test-service"
        assert result["version"] == "1.0.0"
        assert result["timestamp"] is not None
        assert result["environment"] is not None


class TestHealthChecker:
    """Test HealthChecker class"""

    # Define patch paths as class constants
    PATH_GET_DB_HEALTH = f'{health_checks.__name__}.get_database_health'
    PATH_GET_MANAGER = f'{dynamodb_connection.__name__}.get_dynamodb_manager'

    @pytest.fixture
    def health_checker(self):
        """Create a HealthChecker instance"""
        return HealthChecker("test-service", "1.0.0", "test")

    def test_basic_health_check(self, health_checker):
        """Test basic health check"""
        result = health_checker.basic_health_check()

        assert result["status"] == "healthy"
        assert result["service"] == "test-service"
        assert result["version"] == "1.0.0"
        assert result["checks"]["api"] == "ok"
        assert result["checks"]["service"] == "running"

    def test_liveness_check(self, health_checker):
        """Test liveness check"""
        result = health_checker.liveness_check()

        assert result["status"] == "alive"
        assert result["service"] == "test-service"
        assert result["checks"]["api"] == "ok"
        assert result["checks"]["service"] == "alive"

    def test_readiness_check_success(self, health_checker):
        """Test successful readiness check"""
        with patch(self.PATH_GET_DB_HEALTH) as mock_db_health:
            mock_db_health.return_value = True

            result = health_checker.readiness_check()

            assert result["status"] == "ready"
            assert result["service"] == "test-service"
            assert result["checks"]["api"] == "ok"
            assert result["checks"]["database"] == "ok"
            assert result["checks"]["service"] == "ready"

    def test_readiness_check_database_failure(self, health_checker):
        """Test readiness check when database is unhealthy"""
        with patch(self.PATH_GET_DB_HEALTH) as mock_db_health:
            mock_db_health.return_value = False

            with pytest.raises(HTTPException) as exc_info:
                health_checker.readiness_check()

            assert exc_info.value.status_code == 503
            assert "Database not ready" in str(exc_info.value.detail)

    def test_readiness_check_exception(self, health_checker):
        """Test readiness check when exception occurs"""
        with patch(self.PATH_GET_DB_HEALTH) as mock_db_health:
            mock_db_health.side_effect = Exception("Database connection failed")

            with pytest.raises(HTTPException) as exc_info:
                health_checker.readiness_check()

            assert exc_info.value.status_code == 503
            assert "Service not ready" in str(exc_info.value.detail)

    def test_database_health_check_success(self, health_checker):
        """Test successful database health check"""
        with patch(self.PATH_GET_DB_HEALTH) as mock_db_health:
            mock_db_health.return_value = True

            result = health_checker.database_health_check()

            assert result["status"] == "healthy"
            assert result["service"] == "test-service-database"
            assert result["database"]["status"] == "healthy"
            assert result["database"]["connection"] == "ok"

    def test_database_health_check_failure(self, health_checker):
        """Test database health check when database is unhealthy"""
        with patch(self.PATH_GET_DB_HEALTH) as mock_db_health:
            mock_db_health.return_value = False

            with pytest.raises(HTTPException) as exc_info:
                health_checker.database_health_check()

            assert exc_info.value.status_code == 503
            assert "Database unhealthy" in str(exc_info.value.detail)

    def test_database_health_check_exception(self, health_checker):
        """Test database health check when exception occurs"""
        with patch(self.PATH_GET_DB_HEALTH) as mock_db_health:
            mock_db_health.side_effect = Exception("Database connection failed")

            with pytest.raises(HTTPException) as exc_info:
                health_checker.database_health_check()

            assert exc_info.value.status_code == 503
            assert "Database health check failed" in str(exc_info.value.detail)


class TestCreateHealthChecker:
    """Test create_health_checker function"""

    def test_create_health_checker(self):
        """Test creating a health checker via factory function"""
        checker = create_health_checker("test-service", "2.0.0")

        assert isinstance(checker, HealthChecker)
        assert checker.service_name == "test-service"
        assert checker.version == "2.0.0"


class TestGetDatabaseHealth:
    """Test get_database_health function"""

    # Define patch paths as class constants
    PATH_GET_DB_HEALTH = f'{health_checks.__name__}.get_database_health'
    PATH_GET_MANAGER = f'{dynamodb_connection.__name__}.get_dynamodb_manager'

    def test_get_database_health_success(self):
        """Test successful database health check"""
        with patch(self.PATH_GET_MANAGER) as mock_get_manager:
            mock_manager = MagicMock()
            mock_manager.health_check.return_value = True
            mock_get_manager.return_value = mock_manager

            result = get_database_health()

            assert result is True

    def test_get_database_health_failure(self):
        """Test database health check when database is unhealthy"""
        with patch(self.PATH_GET_MANAGER) as mock_get_manager:
            mock_manager = MagicMock()
            mock_manager.health_check.return_value = False
            mock_get_manager.return_value = mock_manager

            result = get_database_health()

            assert result is False

    def test_get_database_health_exception(self):
        """Test database health check when exception occurs"""
        with patch(self.PATH_GET_MANAGER) as mock_get_manager:
            mock_manager = MagicMock()
            mock_manager.health_check.side_effect = Exception("Connection failed")
            mock_get_manager.return_value = mock_manager

            result = get_database_health()

            assert result is False