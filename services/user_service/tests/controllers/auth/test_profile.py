import pytest
from fastapi import HTTPException, status
from unittest.mock import AsyncMock, patch, MagicMock
from controllers.auth.profile import get_profile, update_profile, get_current_user
from api_models.auth.profile import UserProfileUpdateRequest
from fastapi.security import HTTPAuthorizationCredentials
from user_exceptions import UserNotFoundException, TokenExpiredException, UserAlreadyExistsException
from datetime import datetime

@pytest.mark.asyncio
async def test_get_profile_valid_token():
    mock_user = MagicMock()
    mock_user.username = "john_doe"
    mock_user.email = "john@example.com"
    mock_user.first_name = "John"
    mock_user.last_name = "Doe"
    mock_user.phone = "+1234567890"
    mock_user.date_of_birth = "1990-01-01"
    mock_user.marketing_emails_consent = True
    mock_user.created_at = datetime(2024, 1, 1, 0, 0, 0)
    mock_user.updated_at = datetime(2024, 1, 2, 0, 0, 0)

    result = await get_profile(current_user=mock_user)
    assert result.username == "john_doe"
    assert result.email == "john@example.com"

@pytest.mark.asyncio
async def test_update_profile_valid():
    mock_user = MagicMock()
    mock_user.username = "john_doe"
    mock_user.email = "john@example.com"
    mock_user.first_name = "John"
    mock_user.last_name = "Doe"
    mock_user.phone = "+1234567890"
    mock_user.date_of_birth = "1990-01-01"
    mock_user.marketing_emails_consent = True
    mock_user.created_at = datetime(2024, 1, 1, 0, 0, 0)
    mock_user.updated_at = datetime(2024, 1, 2, 0, 0, 0)

    mock_updated_user = MagicMock()
    mock_updated_user.username = "john_doe"
    mock_updated_user.email = "john.new@example.com"
    mock_updated_user.first_name = "John"
    mock_updated_user.last_name = "Doe"
    mock_updated_user.phone = "+1234567890"
    mock_updated_user.date_of_birth = "1990-01-01"
    mock_updated_user.marketing_emails_consent = True
    mock_updated_user.created_at = datetime(2024, 1, 1, 0, 0, 0)
    mock_updated_user.updated_at = datetime(2024, 1, 2, 0, 0, 0)

    mock_user_dao = MagicMock()
    mock_user_dao.update_user = MagicMock(return_value=mock_updated_user)
    mock_user_dao.get_user_by_email = MagicMock(return_value=None)  # Email is unique

    profile_data = UserProfileUpdateRequest(
        email="john.new@example.com",
        first_name="John",
        last_name="Doe",
        phone="+1234567890",
        date_of_birth="1990-01-01"
    )
    result = await update_profile(profile_data, current_user=mock_user, user_dao=mock_user_dao)
    assert result.message == "Profile updated successfully"
    assert result.user.username == "john_doe"
    assert result.user.email == "john.new@example.com"

@pytest.mark.asyncio
async def test_update_profile_email_in_use():
    mock_user = MagicMock()
    mock_user.username = "john_doe"
    mock_user.email = "john@example.com"
    mock_user.first_name = "John"
    mock_user.last_name = "Doe"
    mock_user.phone = "+1234567890"
    mock_user.date_of_birth = "1990-01-01"
    mock_user.marketing_emails_consent = True
    mock_user.created_at = datetime(2024, 1, 1, 0, 0, 0)
    mock_user.updated_at = datetime(2024, 1, 2, 0, 0, 0)

    mock_user_dao = MagicMock()
    mock_user_dao.get_user_by_email = MagicMock(return_value=MagicMock())  # Email already exists

    profile_data = UserProfileUpdateRequest(
        email="existing@example.com",
        first_name="John",
        last_name="Doe",
        phone="+1234567890",
        date_of_birth="1990-01-01"
    )
    with pytest.raises(UserAlreadyExistsException):
        await update_profile(profile_data, current_user=mock_user, user_dao=mock_user_dao)

@pytest.mark.asyncio
async def test_update_profile_unauthorized():
    mock_user = MagicMock()
    mock_user.username = "john_doe"
    mock_user.email = "john@example.com"
    mock_user.first_name = "John"
    mock_user.last_name = "Doe"
    mock_user.phone = "+1234567890"
    mock_user.date_of_birth = "1990-01-01"
    mock_user.marketing_emails_consent = True
    mock_user.created_at = datetime(2024, 1, 1, 0, 0, 0)
    mock_user.updated_at = datetime(2024, 1, 2, 0, 0, 0)

    mock_user_dao = MagicMock()
    mock_user_dao.update_user = MagicMock(return_value=None)

    profile_data = UserProfileUpdateRequest(
        email="john@example.com",
        first_name="John",
        last_name="Doe",
        phone="+1234567890",
        date_of_birth="1990-01-01"
    )
    with pytest.raises(UserNotFoundException) as exc_info:
        await update_profile(profile_data, current_user=mock_user, user_dao=mock_user_dao)
    assert "User 'john_doe' not found" in str(exc_info.value)

@pytest.mark.asyncio
async def test_update_profile_user_not_found():
    mock_user = MagicMock()
    mock_user.username = "john_doe"
    mock_user.email = "john@example.com"
    mock_user.first_name = "John"
    mock_user.last_name = "Doe"
    mock_user.phone = "+1234567890"
    mock_user.date_of_birth = "1990-01-01"
    mock_user.marketing_emails_consent = True
    mock_user.created_at = datetime(2024, 1, 1, 0, 0, 0)
    mock_user.updated_at = datetime(2024, 1, 2, 0, 0, 0)

    mock_user_dao = MagicMock()
    mock_user_dao.update_user = MagicMock(return_value=None)

    profile_data = UserProfileUpdateRequest(
        email="john@example.com",
        first_name="John",
        last_name="Doe",
        phone="+1234567890",
        date_of_birth="1990-01-01"
    )
    with pytest.raises(UserNotFoundException) as exc_info:
        await update_profile(profile_data, current_user=mock_user, user_dao=mock_user_dao)
    assert "User 'john_doe' not found" in str(exc_info.value)

@pytest.mark.asyncio
async def test_update_profile_database_error():
    mock_user = MagicMock()
    mock_user.username = "john_doe"
    mock_user.email = "john@example.com"
    mock_user.first_name = "John"
    mock_user.last_name = "Doe"
    mock_user.phone = "+1234567890"
    mock_user.date_of_birth = "1990-01-01"
    mock_user.marketing_emails_consent = True
    mock_user.created_at = datetime(2024, 1, 1, 0, 0, 0)
    mock_user.updated_at = datetime(2024, 1, 2, 0, 0, 0)

    mock_user_dao = MagicMock()
    mock_user_dao.update_user = MagicMock(side_effect=Exception("Database error"))

    profile_data = UserProfileUpdateRequest(
        email="john@example.com",
        first_name="John",
        last_name="Doe",
        phone="+1234567890",
        date_of_birth="1990-01-01"
    )
    with pytest.raises(HTTPException) as exc_info:
        await update_profile(profile_data, current_user=mock_user, user_dao=mock_user_dao)
    assert exc_info.value.status_code == 500

@pytest.mark.asyncio
async def test_get_current_user_valid():
    mock_creds = MagicMock()
    mock_creds.credentials = "valid.jwt.token"
    mock_user_dao = MagicMock()
    mock_user = MagicMock()
    mock_user.username = "john_doe"
    mock_user_dao.get_user_by_username = MagicMock(return_value=mock_user)
    with patch("controllers.auth.profile.verify_access_token", return_value="john_doe"):
        result = await get_current_user(credentials=mock_creds, user_dao=mock_user_dao)
        assert result.username == "john_doe"

@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    mock_creds = MagicMock()
    mock_creds.credentials = "invalid.jwt.token"
    mock_user_dao = MagicMock()
    with patch("controllers.auth.profile.verify_access_token", return_value=None):
        with pytest.raises(TokenExpiredException):
            await get_current_user(credentials=mock_creds, user_dao=mock_user_dao)

@pytest.mark.asyncio
async def test_get_current_user_user_not_found():
    mock_creds = MagicMock()
    mock_creds.credentials = "valid.jwt.token"
    mock_user_dao = MagicMock()
    with patch("controllers.auth.profile.verify_access_token", return_value="john_doe"), \
         patch.object(mock_user_dao, "get_user_by_username", MagicMock(return_value=None)):
        with pytest.raises(UserNotFoundException):
            await get_current_user(credentials=mock_creds, user_dao=mock_user_dao)

@pytest.mark.asyncio
async def test_get_current_user_verify_token_exception():
    mock_creds = MagicMock()
    mock_creds.credentials = "invalid.jwt.token"
    mock_user_dao = MagicMock()
    with patch("controllers.auth.profile.verify_access_token", side_effect=Exception("Token error")):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=mock_creds, user_dao=mock_user_dao)
        assert exc_info.value.status_code == 401

@pytest.mark.asyncio
async def test_get_current_user_user_dao_exception():
    mock_creds = MagicMock()
    mock_creds.credentials = "valid.jwt.token"
    mock_user_dao = MagicMock()
    with patch("controllers.auth.profile.verify_access_token", return_value="john_doe"), \
         patch.object(mock_user_dao, "get_user_by_username", MagicMock(side_effect=Exception("DAO error"))):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=mock_creds, user_dao=mock_user_dao)
        assert exc_info.value.status_code == 401
