import os
import pytest
from fastapi import HTTPException, status
from unittest.mock import AsyncMock, patch, MagicMock
from controllers.auth.login import login_user
from api_models.auth.login import UserLoginRequest
from common.exceptions.shared_exceptions import CNOPInvalidCredentialsException, CNOPUserNotFoundException
import pydantic

# Test constants
TEST_JWT_SECRET = "test-secret-key-for-unit-tests-at-least-32-chars-long"

# Set JWT_SECRET_KEY for all tests
os.environ["JWT_SECRET_KEY"] = TEST_JWT_SECRET


def create_mock_request(request_id="test-request-id"):
    """Helper function to create a mock request object with headers"""
    mock_request = MagicMock()
    mock_request.headers = {"X-Request-ID": request_id}
    return mock_request

def test_login_success():
    # Mock user DAO
    mock_user_dao = MagicMock()
    mock_user = MagicMock()
    mock_user.username = "testuser"
    mock_user.role = "user"
    mock_user_dao.authenticate_user.return_value = mock_user

    # Test data
    login_data = UserLoginRequest(username="testuser", password="ValidPass123!@#")

    # Call the function
    result = login_user(login_data, request=create_mock_request(), user_dao=mock_user_dao)

    # Verify result
    assert result.message == "Login successful"
    assert result.data.access_token is not None
    assert result.data.token_type == "bearer"
    assert result.data.expires_in == 3600

def test_login_invalid_credentials():
    # Mock user DAO to return None (invalid credentials)
    mock_user_dao = MagicMock()
    mock_user_dao.authenticate_user.return_value = None

    # Test data
    login_data = UserLoginRequest(username="testuser", password="ValidPass123!@#")

    # Test that the function raises the correct exception
    with pytest.raises(CNOPInvalidCredentialsException) as exc_info:
        login_user(login_data, request=create_mock_request(), user_dao=mock_user_dao)

    assert "Invalid credentials for user 'testuser'" in str(exc_info.value)

def test_login_user_not_found():
    # Mock user DAO to raise UserNotFoundException
    mock_user_dao = MagicMock()
    mock_user_dao.authenticate_user.side_effect = CNOPUserNotFoundException("User not found")

    # Test data
    login_data = UserLoginRequest(username="nonexistent", password="ValidPass123!@#")

    # Test that the function raises the correct exception
    with pytest.raises(CNOPUserNotFoundException) as exc_info:
        login_user(login_data, request=create_mock_request(), user_dao=mock_user_dao)

    assert "User not found" in str(exc_info.value)

@pytest.mark.asyncio
async def test_login_missing_input():
    # Missing password
    with pytest.raises(pydantic.ValidationError):
        UserLoginRequest(username="john_doe")

@pytest.mark.asyncio
async def test_login_database_error():
    mock_user_dao = MagicMock()
    mock_user_dao.authenticate_user = MagicMock(side_effect=Exception("db error"))
    login_data = UserLoginRequest(username="john_doe", password="Password123!")

    # Database errors should bubble up as exceptions
    with pytest.raises(Exception) as exc_info:
        login_user(login_data, request=create_mock_request(), user_dao=mock_user_dao)
    assert "db error" in str(exc_info.value)
