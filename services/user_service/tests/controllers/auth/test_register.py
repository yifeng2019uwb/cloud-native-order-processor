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
    assert "Username 'newuser' already exists" in str(exc_info.value.detail)

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
    assert "Email 'newuser@example.com' already exists" in str(exc_info.value.detail)

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
async def test_register_unexpected_error():
    mock_user_dao = AsyncMock()
    mock_user_dao.get_user_by_username = AsyncMock(return_value=None)
    mock_user_dao.get_user_by_email = AsyncMock(return_value=None)
    mock_user_dao.create_user = AsyncMock(side_effect=Exception("Unexpected error"))
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
async def test_register_missing_input():
    # Missing required fields
    with pytest.raises(pydantic.ValidationError):
        UserRegistrationRequest(
            username="newuser",
            # Missing email and password
        )

@pytest.mark.asyncio
async def test_register_invalid_email():
    with pytest.raises(pydantic.ValidationError):
        UserRegistrationRequest(
            username="newuser",
            email="invalid-email",
            password="ValidPass123!@#",
            first_name="New",
            last_name="User",
            phone="+1-555-123-4567"
        )

@pytest.mark.asyncio
async def test_register_weak_password():
    with pytest.raises(pydantic.ValidationError):
        UserRegistrationRequest(
            username="newuser",
            email="newuser@example.com",
            password="weak",
            first_name="New",
            last_name="User",
            phone="+1-555-123-4567"
        )

@pytest.mark.asyncio
async def test_register_invalid_phone():
    with pytest.raises(pydantic.ValidationError):
        UserRegistrationRequest(
            username="newuser",
            email="newuser@example.com",
            password="ValidPass123!@#",
            first_name="New",
            last_name="User",
            phone="invalid-phone"
        )

@pytest.mark.asyncio
async def test_register_future_date_of_birth():
    with pytest.raises(pydantic.ValidationError):
        UserRegistrationRequest(
            username="newuser",
            email="newuser@example.com",
            password="ValidPass123!@#",
            first_name="New",
            last_name="User",
            phone="+1-555-123-4567",
            date_of_birth="2030-01-01"
        )