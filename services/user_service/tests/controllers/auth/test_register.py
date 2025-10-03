import pytest
import pydantic
from fastapi import HTTPException, status
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import date, timedelta
from controllers.auth.register import register_user
from api_models.auth.registration import UserRegistrationRequest
from user_exceptions import CNOPUserAlreadyExistsException, CNOPUserValidationException

from common.exceptions.shared_exceptions import (
    CNOPEntityAlreadyExistsException,
    CNOPInternalServerException
)


def create_mock_request(request_id="test-request-id"):
    """Helper function to create a mock request object with headers"""
    mock_request = MagicMock()
    mock_request.headers = {"X-Request-ID": request_id}
    return mock_request

def test_register_success():
    from uuid import uuid4

    mock_user_dao = MagicMock()
    mock_user_dao.get_user_by_username = MagicMock(return_value=None)
    mock_user_dao.get_user_by_email = MagicMock(return_value=None)
    mock_user = MagicMock()
    mock_user.username = "newuser"
    mock_user_dao.create_user = MagicMock(return_value=mock_user)

    # Mock balance_dao
    mock_balance_dao = MagicMock()
    mock_balance_dao.create_balance = MagicMock()

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
    result = register_user(reg_data, request=mock_request, user_dao=mock_user_dao, balance_dao=mock_balance_dao)
    assert result.message == "User registered successfully"
    assert result.success is True

def test_register_username_exists():
    mock_user_dao = MagicMock()
    mock_user_dao.get_user_by_username = MagicMock(return_value=MagicMock())
    mock_user_dao.get_user_by_email = MagicMock(return_value=None)
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
    with pytest.raises(CNOPUserAlreadyExistsException) as exc_info:
        register_user(reg_data, request=mock_request, user_dao=mock_user_dao)
    assert "Username 'newuser' already exists" in exc_info.value.message

def test_register_email_exists():
    mock_user_dao = MagicMock()
    mock_user_dao.get_user_by_username = MagicMock(return_value=None)
    mock_user_dao.get_user_by_email = MagicMock(return_value=MagicMock())
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
    with pytest.raises(CNOPUserAlreadyExistsException) as exc_info:
        register_user(reg_data, request=mock_request, user_dao=mock_user_dao)
    assert "Email 'newuser@example.com' already exists" in exc_info.value.message

def test_register_validation_error():
    mock_user_dao = MagicMock()
    mock_user_dao.get_user_by_username = MagicMock(return_value=None)
    mock_user_dao.get_user_by_email = MagicMock(return_value=None)
    mock_user_dao.create_user = MagicMock(side_effect=CNOPEntityAlreadyExistsException("Some validation error"))
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
    with pytest.raises(CNOPInternalServerException) as exc_info:
        register_user(reg_data, request=mock_request, user_dao=mock_user_dao)
    assert "CNOPEntityAlreadyExistsException: Some validation error" in str(exc_info.value)

@pytest.mark.asyncio
async def test_register_unexpected_error():
    mock_user_dao = MagicMock()
    mock_user_dao.get_user_by_username = MagicMock(return_value=None)
    mock_user_dao.get_user_by_email = MagicMock(return_value=None)
    mock_user_dao.create_user = MagicMock(side_effect=Exception("Unexpected error"))
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
    with pytest.raises(CNOPInternalServerException) as exc_info:
        await register_user(reg_data, request=mock_request, user_dao=mock_user_dao)
    assert "An internal server error occurred. Please try again later. during registration: Unexpected error" in str(exc_info.value)

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
    # Validation now happens at model level
    with pytest.raises(CNOPUserValidationException, match="Phone number must contain 10-15 digits"):
        UserRegistrationRequest(
            username="johndoe",
            email="test@example.com",
            password="SecurePassword123!",
            first_name="John",
            last_name="Doe",
            phone="123"  # Too short - will be rejected at model level
        )

@pytest.mark.asyncio
async def test_register_future_date_of_birth():
    # Validation now happens at model level
    future_date = date.today() + timedelta(days=1)
    with pytest.raises(CNOPUserValidationException, match="User must be at least 13 years old"):
        UserRegistrationRequest(
            username="johndoe",
            email="test@example.com",
            password="SecurePassword123!",
            first_name="John",
            last_name="Doe",
            date_of_birth=future_date  # Future date - will be rejected at model level
        )