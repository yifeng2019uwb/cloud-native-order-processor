import pytest
from fastapi import HTTPException, status
from unittest.mock import AsyncMock, patch, MagicMock
from controllers.auth.profile import get_profile, update_profile, get_current_user
from api_models.auth.profile import UserProfileUpdateRequest
from fastapi.security import HTTPAuthorizationCredentials
from common.exceptions.shared_exceptions import (
    CNOPUserNotFoundException,
    CNOPEntityNotFoundException
)
from user_exceptions import CNOPUserAlreadyExistsException
from datetime import datetime, timezone


def create_mock_request(request_id="test-request-id"):
    """Helper function to create a mock request object with headers"""
    mock_request = MagicMock()
    mock_request.headers = {"X-Request-ID": request_id}
    return mock_request

def test_get_profile_success():
    mock_user = MagicMock()
    mock_user.username = "testuser"
    mock_user.email = "test@example.com"
    mock_user.first_name = "Test"
    mock_user.last_name = "User"
    mock_user.phone = "+1234567890"
    mock_user.date_of_birth = datetime(1990, 1, 1).date()
    mock_user.marketing_emails_consent = True
    mock_user.created_at = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    mock_user.updated_at = datetime(2024, 1, 2, 0, 0, 0, tzinfo=timezone.utc)

    # Call the function
    result = get_profile(request=create_mock_request(), current_user=mock_user)

    # Verify result
    assert result.username == "testuser"
    assert result.email == "test@example.com"
    assert result.first_name == "Test"
    assert result.last_name == "User"
    assert result.phone == "+1234567890"
    assert result.date_of_birth == datetime(1990, 1, 1).date()
    assert result.marketing_emails_consent is True
    assert result.created_at == datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    assert result.updated_at == datetime(2024, 1, 2, 0, 0, 0, tzinfo=timezone.utc)

def test_update_profile_success():
    mock_user = MagicMock()
    mock_user.username = "john_doe"
    mock_user.email = "john@example.com"
    mock_user.password = "[HASHED]"
    mock_user.first_name = "John"
    mock_user.last_name = "Doe"
    mock_user.phone = "+1234567890"
    mock_user.date_of_birth = "1990-01-01"
    mock_user.marketing_emails_consent = True
    mock_user.role = "customer"
    mock_user.created_at = datetime(2024, 1, 1, 0, 0, 0)
    mock_user.updated_at = datetime(2024, 1, 2, 0, 0, 0)

    mock_updated_user = MagicMock()
    mock_updated_user.username = "john_doe"
    mock_updated_user.email = "john.new@example.com"
    mock_updated_user.password = "[HASHED]"
    mock_updated_user.first_name = "John"
    mock_updated_user.last_name = "Doe"
    mock_updated_user.phone = "+1234567890"
    mock_updated_user.date_of_birth = "1990-01-01"
    mock_updated_user.marketing_emails_consent = True
    mock_updated_user.role = "customer"
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
    result = update_profile(profile_data, request=create_mock_request(), current_user=mock_user, user_dao=mock_user_dao)
    assert result.message == "Profile updated successfully"
    assert result.user.username == "john_doe"
    assert result.user.email == "john.new@example.com"

def test_update_profile_email_in_use():
    """Test when user tries to update profile with email already taken by another user"""
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
    other_user = MagicMock()
    other_user.username = "other_user"
    mock_user_dao.get_user_by_email = MagicMock(return_value=other_user)

    profile_data = UserProfileUpdateRequest(
        email="existing@example.com",
        first_name="John",
        last_name="Doe",
        phone="+1234567890",
        date_of_birth="1990-01-01"
    )

    with pytest.raises(CNOPUserAlreadyExistsException) as exc_info:
        update_profile(profile_data, request=create_mock_request(), current_user=mock_user, user_dao=mock_user_dao)
    assert "Email 'existing@example.com' already exists" in str(exc_info.value)



def test_update_profile_user_not_found():
    mock_user = MagicMock()
    mock_user.username = "john_doe"
    mock_user.email = "john@example.com"
    mock_user.password = "[HASHED]"
    mock_user.first_name = "John"
    mock_user.last_name = "Doe"
    mock_user.phone = "+1234567890"
    mock_user.date_of_birth = "1990-01-01"
    mock_user.marketing_emails_consent = True
    mock_user.role = "customer"
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
    with pytest.raises(CNOPEntityNotFoundException) as exc_info:
        update_profile(profile_data, request=create_mock_request(), current_user=mock_user, user_dao=mock_user_dao)
    assert "User 'john_doe' not found" in str(exc_info.value)

def test_update_profile_with_own_email():
    """Test that user can update profile with their own email (no uniqueness conflict)"""
    mock_user = MagicMock()
    mock_user.username = "john_doe"
    mock_user.email = "john@example.com"
    mock_user.password = "[HASHED]"
    mock_user.first_name = "John"
    mock_user.last_name = "Doe"
    mock_user.phone = "+1234567890"
    mock_user.date_of_birth = "1990-01-01"
    mock_user.marketing_emails_consent = True
    mock_user.role = "customer"
    mock_user.created_at = datetime(2024, 1, 1, 0, 0, 0)
    mock_user.updated_at = datetime(2024, 1, 2, 0, 0, 0)

    updated_user = MagicMock()
    updated_user.username = "john_doe"
    updated_user.email = "john@example.com"  # Same email
    updated_user.password = "[HASHED]"
    updated_user.first_name = "John"
    updated_user.last_name = "Doe"
    updated_user.phone = "+1234567890"
    updated_user.date_of_birth = "1990-01-01"
    updated_user.role = "customer"
    updated_user.created_at = datetime(2024, 1, 1, 0, 0, 0)
    updated_user.updated_at = datetime(2024, 1, 2, 0, 0, 0)

    mock_user_dao = MagicMock()
    # get_user_by_email should not be called since email is the same
    mock_user_dao.get_user_by_email = MagicMock()
    mock_user_dao.update_user = MagicMock(return_value=updated_user)

    profile_data = UserProfileUpdateRequest(
        email="john@example.com",  # Same email as current user
        first_name="John",
        last_name="Doe",
        phone="+1234567890",
        date_of_birth="1990-01-01"
    )

    result = update_profile(profile_data, request=create_mock_request(), current_user=mock_user, user_dao=mock_user_dao)
    assert result.message == "Profile updated successfully"
    assert result.user.username == "john_doe"
    assert result.user.email == "john@example.com"

    mock_user_dao.get_user_by_email.assert_not_called()

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
        await update_profile(profile_data, request=create_mock_request(), current_user=mock_user, user_dao=mock_user_dao)
    assert exc_info.value.status_code == 500
