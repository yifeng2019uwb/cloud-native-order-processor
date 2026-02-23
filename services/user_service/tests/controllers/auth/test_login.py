"""
Tests for login controller - Focus on business logic
"""
import os
import pytest
from fastapi import HTTPException, status
from unittest.mock import AsyncMock, patch, MagicMock
from controllers.auth.login import login_user
from api_models.auth.login import UserLoginRequest, LoginResponse
from common.exceptions.shared_exceptions import CNOPInvalidCredentialsException, CNOPUserNotFoundException
from common.exceptions.shared_exceptions import CNOPInternalServerException

# Test constants
TEST_JWT_SECRET = "test-secret-key-for-unit-tests-at-least-32-chars-long"
TEST_REQUEST_ID = "test-request-id"
TEST_USERNAME = "testuser"
TEST_USERNAME_NONEXISTENT = "nonexistent"
TEST_PASSWORD = "ValidPass123!@#"
TEST_USER_ROLE = "user"
TEST_TOKEN_TYPE = "bearer"

# Set JWT_SECRET_KEY for all tests
os.environ["JWT_SECRET_KEY"] = TEST_JWT_SECRET

def create_mock_request(request_id=TEST_REQUEST_ID):
    """Helper function to create a mock request object with headers and client (JSON-serializable for audit logger)."""
    mock_request = MagicMock()
    mock_request.headers = {"X-Request-ID": request_id}
    # request.client.host and headers.get(User-Agent) are passed to audit logger and must be JSON-serializable (no MagicMock)
    mock_request.client = MagicMock()
    mock_request.client.host = "127.0.0.1"
    return mock_request


def test_login_success():
    """Test successful login"""
    # Mock user DAO
    mock_user_dao = MagicMock()
    mock_user = MagicMock()
    mock_user.username = TEST_USERNAME
    mock_user.role = TEST_USER_ROLE
    mock_user_dao.authenticate_user.return_value = mock_user

    # Test data
    login_data = UserLoginRequest(username=TEST_USERNAME, password=TEST_PASSWORD)

    # Call the function
    result = login_user(login_data, request=create_mock_request(), user_dao=mock_user_dao)

    # Verify result
    assert isinstance(result, LoginResponse)
    assert result.access_token is not None
    assert result.token_type == TEST_TOKEN_TYPE
    assert result.expires_in == 3600


def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    # Mock user DAO to return None (invalid credentials)
    mock_user_dao = MagicMock()
    mock_user_dao.authenticate_user.return_value = None

    # Test data
    login_data = UserLoginRequest(username=TEST_USERNAME, password=TEST_PASSWORD)

    # Call the function and expect exception
    with pytest.raises(CNOPInvalidCredentialsException):
        login_user(login_data, request=create_mock_request(), user_dao=mock_user_dao)


def test_login_user_not_found():
    """Test login when user is not found"""
    # Mock user DAO to raise user not found exception
    mock_user_dao = MagicMock()
    mock_user_dao.authenticate_user.side_effect = CNOPUserNotFoundException("User not found")

    # Test data
    login_data = UserLoginRequest(username=TEST_USERNAME_NONEXISTENT, password=TEST_PASSWORD)

    # Call the function and expect exception
    with pytest.raises(CNOPUserNotFoundException):
        login_user(login_data, request=create_mock_request(), user_dao=mock_user_dao)


def test_login_unexpected_exception_wrapped_internal_error():
    """Ensure unexpected exceptions are wrapped into CNOPInternalServerException."""
    mock_user_dao = MagicMock()
    mock_user_dao.authenticate_user.side_effect = RuntimeError("db down")

    login_data = UserLoginRequest(username=TEST_USERNAME, password=TEST_PASSWORD)

    with pytest.raises(CNOPInternalServerException) as exc:
        login_user(login_data, request=create_mock_request(), user_dao=mock_user_dao)
    assert "Internal server error" in str(exc.value).lower() or "during login" in str(exc.value)