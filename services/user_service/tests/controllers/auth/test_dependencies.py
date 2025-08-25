"""
Tests for auth dependencies module
"""
import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, status
from fastapi.testclient import TestClient

# Import the functions to test
from src.controllers.auth.dependencies import (
    verify_gateway_headers,
    get_current_user,
    get_optional_current_user,
    require_admin_user
)

# Import models
from common.entities.user import UserResponse


def test_verify_gateway_headers_valid():
    """Test valid gateway headers"""
    mock_request = MagicMock()

    # Test with valid headers
    result = verify_gateway_headers(
        request=mock_request,
        x_source="gateway",
        x_auth_service="auth-service",
        x_user_id="user123",
        x_user_role="user"
    )

    assert result == "user123"

def test_verify_gateway_headers_invalid_source():
    """Test invalid source header"""
    mock_request = MagicMock()

    with pytest.raises(HTTPException) as exc_info:
        verify_gateway_headers(
            request=mock_request,
            x_source="invalid",
            x_auth_service="auth-service",
            x_user_id="user123",
            x_user_role="user"
        )

    assert exc_info.value.status_code == 403
    assert "Invalid request source" in str(exc_info.value.detail)

def test_verify_gateway_headers_invalid_auth_service():
    """Test invalid auth service header"""
    mock_request = MagicMock()

    with pytest.raises(HTTPException) as exc_info:
        verify_gateway_headers(
            request=mock_request,
            x_source="gateway",
            x_auth_service="invalid",
            x_user_id="user123",
            x_user_role="user"
        )

    assert exc_info.value.status_code == 403
    assert "Invalid authentication service" in str(exc_info.value.detail)

def test_verify_gateway_headers_missing_user_id():
    """Test missing user ID header"""
    mock_request = MagicMock()

    with pytest.raises(HTTPException) as exc_info:
        verify_gateway_headers(
            request=mock_request,
            x_source="gateway",
            x_auth_service="auth-service",
            x_user_id=None,
            x_user_role="user"
        )

    assert exc_info.value.status_code == 401
    assert "User authentication required" in str(exc_info.value.detail)

def test_get_current_user_success():
    """Test successful user retrieval"""
    mock_user_dao = MagicMock()
    mock_user = MagicMock()
    mock_user.username = "testuser"
    mock_user.email = "test@example.com"
    mock_user.first_name = "Test"
    mock_user.last_name = "User"
    mock_user.phone = "+1234567890"
    mock_user.date_of_birth = "1990-01-01"
    mock_user.marketing_emails_consent = True
    mock_user.role = "user"
    mock_user.created_at = "2024-01-01T00:00:00Z"
    mock_user.updated_at = "2024-01-02T00:00:00Z"

    mock_user_dao.get_user_by_username.return_value = mock_user

    result = get_current_user(username="testuser", user_dao=mock_user_dao)

    assert result.username == "testuser"
    assert result.email == "test@example.com"
    assert result.first_name == "Test"
    assert result.last_name == "User"
    assert result.role == "user"

def test_get_current_user_not_found():
    """Test user not found"""
    mock_user_dao = MagicMock()
    mock_user_dao.get_user_by_username.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(username="nonexistent", user_dao=mock_user_dao)

    assert exc_info.value.status_code == 401
    assert "User not found" in str(exc_info.value.detail)

def test_get_current_user_database_error():
    """Test database error during user retrieval"""
    mock_user_dao = MagicMock()
    mock_user_dao.get_user_by_username.side_effect = Exception("Database error")

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(username="testuser", user_dao=mock_user_dao)

    assert exc_info.value.status_code == 500
    assert "Failed to get user information" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_get_optional_current_user_with_headers():
    """Test get_optional_current_user with valid headers"""
    mock_user = MagicMock()
    mock_user.username = "john_doe123"
    mock_user.email = "john.doe@example.com"
    mock_user.first_name = "John"
    mock_user.last_name = "Doe"
    mock_user.phone = "+1-555-123-4567"
    mock_user.date_of_birth = None
    mock_user.marketing_emails_consent = False
    mock_user.role = "customer"
    mock_user.created_at = "2025-07-09T10:30:00Z"
    mock_user.updated_at = "2025-07-09T10:30:00Z"

    mock_user_dao = MagicMock()
    mock_user_dao.get_user_by_username = MagicMock(return_value=mock_user)

    mock_request = MagicMock()

    result = get_optional_current_user(
        request=mock_request,
        x_source="gateway",
        x_auth_service="auth-service",
        x_user_id="john_doe123",
        x_user_role="customer",
        user_dao=mock_user_dao
    )

    assert result is not None
    assert result.username == "john_doe123"


def test_get_optional_current_user_missing_headers():
    """Test get_optional_current_user with missing headers"""
    mock_user_dao = MagicMock()
    mock_request = MagicMock()

    result = get_optional_current_user(
        request=mock_request,
        x_source=None,
        x_auth_service="auth-service",
        x_user_id="john_doe123",
        x_user_role="customer",
        user_dao=mock_user_dao
    )

    assert result is None


def test_get_optional_current_user_invalid_headers():
    """Test get_optional_current_user with invalid headers"""
    mock_user_dao = MagicMock()
    mock_request = MagicMock()

    result = get_optional_current_user(
        request=mock_request,
        x_source="invalid-source",
        x_auth_service="auth-service",
        x_user_id="john_doe123",
        x_user_role="customer",
        user_dao=mock_user_dao
    )

    assert result is None


def test_get_optional_current_user_user_not_found():
    """Test get_optional_current_user when user not found"""
    mock_user_dao = MagicMock()
    mock_user_dao.get_user_by_username = MagicMock(return_value=None)
    mock_request = MagicMock()

    result = get_optional_current_user(
        request=mock_request,
        x_source="gateway",
        x_auth_service="auth-service",
        x_user_id="john_doe123",
        x_user_role="customer",
        user_dao=mock_user_dao
    )

    assert result is None


def test_get_optional_current_user_exception():
    """Test get_optional_current_user when exception occurs"""
    mock_user_dao = MagicMock()
    mock_user_dao.get_user_by_username = MagicMock(side_effect=Exception("fail"))
    mock_request = MagicMock()

    result = get_optional_current_user(
        request=mock_request,
        x_source="gateway",
        x_auth_service="auth-service",
        x_user_id="john_doe123",
        x_user_role="customer",
        user_dao=mock_user_dao
    )

    assert result is None


def test_require_admin_user():
    """Test require_admin_user function"""
    mock_user = MagicMock()
    mock_user.email = "admin@example.com"

    result = require_admin_user(current_user=mock_user)

    assert result == mock_user