import pytest
from fastapi import HTTPException, status
from unittest.mock import AsyncMock, patch, MagicMock
from controllers.auth.login import login_user
from api_models.auth.login import UserLoginRequest
from common.exceptions.shared_exceptions import InvalidCredentialsException
import pydantic

@pytest.mark.asyncio
async def test_login_valid_credentials_patch_login_only():
    mock_user = MagicMock()
    mock_user.username = "john_doe"
    mock_user.email = "john@example.com"
    mock_user.first_name = "John"
    mock_user.last_name = "Doe"
    mock_user.phone = "+1234567890"
    mock_user.date_of_birth = "1990-01-01"
    mock_user.marketing_emails_consent = True
    mock_user.created_at = "2024-01-01T00:00:00Z"
    mock_user.updated_at = "2024-01-02T00:00:00Z"
    mock_user.role = "user"  # Provide a proper role value

    mock_user_dao = MagicMock()
    mock_user_dao.authenticate_user = MagicMock(return_value=mock_user)

    login_data = UserLoginRequest(username="john_doe", password="Password123!")

    token_dict = {
        "access_token": "token123",
        "token_type": "bearer",
        "expires_in": 3600
    }

    with patch("controllers.auth.login.TokenManager") as mock_token_manager_class:
        mock_token_manager = MagicMock()
        mock_token_manager.create_access_token.return_value = token_dict
        mock_token_manager_class.return_value = mock_token_manager

        result = await login_user(login_data, user_dao=mock_user_dao)

    assert result.data.access_token == "token123"
    assert result.data.token_type == "bearer"
    assert result.data.expires_in == 3600
    assert result.message == "Login successful"
    assert result.success is True

@pytest.mark.asyncio
async def test_login_invalid_credentials():
    mock_user_dao = MagicMock()
    mock_user_dao.authenticate_user = MagicMock(return_value=None)
    login_data = UserLoginRequest(username="john_doe", password="WrongPassword1!")

    with pytest.raises(InvalidCredentialsException) as exc_info:
        await login_user(login_data, user_dao=mock_user_dao)
    assert "Invalid credentials for user 'john_doe'" in str(exc_info.value)

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
        await login_user(login_data, user_dao=mock_user_dao)
    assert "db error" in str(exc_info.value)
