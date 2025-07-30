import pytest
from fastapi import HTTPException, status
from unittest.mock import AsyncMock, patch, MagicMock
from src.controllers.auth.register import register_user
from api_models.auth.registration import UserRegistrationRequest
import pydantic

@pytest.mark.asyncio
async def test_register_success():
    mock_user_dao = AsyncMock()
    mock_user_dao.get_user_by_username = AsyncMock(return_value=None)
    mock_user_dao.get_user_by_email = AsyncMock(return_value=None)
    mock_user = MagicMock()
    mock_user.username = "newuser"
    mock_user_dao.create_user = AsyncMock(return_value=mock_user)
    mock_request = MagicMock()
    mock_request.client = MagicMock(host="127.0.0.1")
    mock_request.headers = {"user-agent": "pytest"}
    reg_data = UserRegistrationRequest(
        username="newuser",
        email="newuser@example.com",
        password="ValidPass123!@#",
        first_name="New",
        last_name="User",
        phone="+1-555-123-4567"
    )
    token_dict = {
        "access_token": "token123",
        "token_type": "bearer",
        "expires_in": 3600
    }
    result = await register_user(reg_data, request=mock_request, user_dao=mock_user_dao)
    assert result.message == "Account created successfully. Please login to continue."
    assert result.success is True

@pytest.mark.asyncio
async def test_register_username_exists():
    mock_user_dao = AsyncMock()
    mock_user_dao.get_user_by_username = AsyncMock(return_value=MagicMock())
    mock_user_dao.get_user_by_email = AsyncMock(return_value=None)
    mock_request = MagicMock()
    mock_request.client = MagicMock(host="127.0.0.1")
    mock_request.headers = {"user-agent": "pytest"}
    reg_data = UserRegistrationRequest(
        username="newuser",
        email="newuser@example.com",
        password="ValidPass123!@#",
        first_name="New",
        last_name="User",
        phone="+1-555-123-4567"
    )
    with pytest.raises(HTTPException) as exc_info:
        await register_user(reg_data, request=mock_request, user_dao=mock_user_dao)
    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert "Username already exists" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_register_email_exists():
    mock_user_dao = AsyncMock()
    mock_user_dao.get_user_by_username = AsyncMock(return_value=None)
    mock_user_dao.get_user_by_email = AsyncMock(return_value=MagicMock())
    mock_request = MagicMock()
    mock_request.client = MagicMock(host="127.0.0.1")
    mock_request.headers = {"user-agent": "pytest"}
    reg_data = UserRegistrationRequest(
        username="newuser",
        email="newuser@example.com",
        password="ValidPass123!@#",
        first_name="New",
        last_name="User",
        phone="+1-555-123-4567"
    )
    with pytest.raises(HTTPException) as exc_info:
        await register_user(reg_data, request=mock_request, user_dao=mock_user_dao)
    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert "Email already exists" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_register_validation_error():
    mock_user_dao = AsyncMock()
    mock_user_dao.get_user_by_username = AsyncMock(return_value=None)
    mock_user_dao.get_user_by_email = AsyncMock(return_value=None)
    mock_user_dao.create_user = AsyncMock(side_effect=ValueError("Some validation error"))
    mock_request = MagicMock()
    mock_request.client = MagicMock(host="127.0.0.1")
    mock_request.headers = {"user-agent": "pytest"}
    reg_data = UserRegistrationRequest(
        username="newuser",
        email="newuser@example.com",
        password="ValidPass123!@#",
        first_name="New",
        last_name="User",
        phone="+1-555-123-4567"
    )
    with pytest.raises(HTTPException) as exc_info:
        await register_user(reg_data, request=mock_request, user_dao=mock_user_dao)
    assert exc_info.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "Some validation error" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_register_db_error():
    mock_user_dao = AsyncMock()
    mock_user_dao.get_user_by_username = AsyncMock(return_value=None)
    mock_user_dao.get_user_by_email = AsyncMock(return_value=None)
    mock_user_dao.create_user = AsyncMock(side_effect=Exception("DB error"))
    mock_request = MagicMock()
    mock_request.client = MagicMock(host="127.0.0.1")
    mock_request.headers = {"user-agent": "pytest"}
    reg_data = UserRegistrationRequest(
        username="newuser",
        email="newuser@example.com",
        password="ValidPass123!@#",
        first_name="New",
        last_name="User",
        phone="+1-555-123-4567"
    )
    with pytest.raises(HTTPException) as exc_info:
        await register_user(reg_data, request=mock_request, user_dao=mock_user_dao)
    assert exc_info.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert "Service is temporarily unavailable" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_register_unexpected_error():
    mock_user_dao = AsyncMock()
    mock_user_dao.get_user_by_username = AsyncMock(side_effect=Exception("Unexpected"))
    mock_user_dao.get_user_by_email = AsyncMock(return_value=None)
    mock_request = MagicMock()
    mock_request.client = MagicMock(host="127.0.0.1")
    mock_request.headers = {"user-agent": "pytest"}
    reg_data = UserRegistrationRequest(
        username="newuser",
        email="newuser@example.com",
        password="ValidPass123!@#",
        first_name="New",
        last_name="User",
        phone="+1-555-123-4567"
    )
    with pytest.raises(HTTPException) as exc_info:
        await register_user(reg_data, request=mock_request, user_dao=mock_user_dao)
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "An unexpected error occurred" in str(exc_info.value.detail)