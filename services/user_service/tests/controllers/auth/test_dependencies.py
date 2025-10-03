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
    get_current_user
)

# Import models
from common.data.entities.user import User


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
