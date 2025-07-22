import pytest
from fastapi import HTTPException, status
from unittest.mock import AsyncMock, patch, MagicMock
from src.controllers.auth.login import login_user
from api_models.auth.login import UserLoginRequest
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

    mock_user_dao = AsyncMock()
    mock_user_dao.authenticate_user = AsyncMock(return_value=mock_user)

    login_data = UserLoginRequest(username="john_doe", password="Password123!")

    token_dict = {
        "access_token": "token123",
        "token_type": "bearer",
        "expires_in": 3600
    }
    with patch("src.controllers.auth.login.create_access_token", return_value=token_dict):
        result = await login_user(login_data, user_dao=mock_user_dao)
        assert result.access_token == "token123"
        assert result.token_type == "bearer"
        assert result.expires_in == 3600
        assert result.user.username == "john_doe"
        assert result.success is True

@pytest.mark.asyncio
async def test_login_invalid_credentials():
    mock_user_dao = AsyncMock()
    mock_user_dao.authenticate_user = AsyncMock(return_value=None)
    login_data = UserLoginRequest(username="john_doe", password="WrongPassword1!")
    with pytest.raises(HTTPException) as exc_info:
        await login_user(login_data, user_dao=mock_user_dao)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_login_missing_input():
    # Missing password
    with pytest.raises(pydantic.ValidationError):
        UserLoginRequest(username="john_doe")

@pytest.mark.asyncio
async def test_login_database_error():
    mock_user_dao = AsyncMock()
    mock_user_dao.authenticate_user = AsyncMock(side_effect=Exception("db error"))
    login_data = UserLoginRequest(username="john_doe", password="Password123!")
    with pytest.raises(HTTPException) as exc_info:
        await login_user(login_data, user_dao=mock_user_dao)
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
