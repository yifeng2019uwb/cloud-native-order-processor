"""
Tests for profile controller - Focus on business logic
"""
import pytest
from fastapi import HTTPException, status
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone
from controllers.auth.profile import get_profile, update_profile
from api_models.auth.profile import UserProfileUpdateRequest, UserProfileResponse, ProfileResponse
from common.data.entities.user import User
from common.exceptions.shared_exceptions import (
    CNOPUserNotFoundException,
    CNOPEntityNotFoundException
)
from user_exceptions import CNOPUserAlreadyExistsException

# Test constants - Only for values reused across multiple tests
TEST_USERNAME = "testuser"
TEST_EMAIL = "test@example.com"
TEST_FIRST_NAME = "Test"
TEST_LAST_NAME = "User"
TEST_PHONE = "+1234567890"
TEST_PASSWORD = "hashed_password"
TEST_USER_ROLE = "user"
TEST_REQUEST_ID = "test-request-id"


def create_mock_request(request_id=TEST_REQUEST_ID):
    """Helper function to create a mock request object with headers"""
    mock_request = MagicMock()
    mock_request.headers = {"X-Request-ID": request_id}
    return mock_request


def test_get_profile_success():
    """Test successful profile retrieval"""
    mock_user = MagicMock()
    mock_user.username = TEST_USERNAME
    mock_user.email = TEST_EMAIL
    mock_user.first_name = TEST_FIRST_NAME
    mock_user.last_name = TEST_LAST_NAME
    mock_user.phone = TEST_PHONE
    mock_user.date_of_birth = datetime(1990, 1, 1).date()
    mock_user.marketing_emails_consent = True
    mock_user.created_at = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    mock_user.updated_at = datetime(2024, 1, 2, 0, 0, 0, tzinfo=timezone.utc)

    # Call the function
    result = get_profile(request=create_mock_request(), current_user=mock_user)

    # Verify result using constants to avoid human error in assertions
    assert isinstance(result, UserProfileResponse)
    assert result.username == TEST_USERNAME
    assert result.email == TEST_EMAIL
    assert result.first_name == TEST_FIRST_NAME
    assert result.last_name == TEST_LAST_NAME


def test_update_profile_success():
    """Test successful profile update"""
    # Local test variables - test data can be hardcoded
    username = "john_doe"
    original_email = "john@example.com"
    original_first_name = "John"
    original_last_name = "Doe"
    updated_email = "john.updated@example.com"
    updated_first_name = "John Updated"
    updated_last_name = "Doe Updated"

    # Create a real User object for current_user
    mock_user = User(
        username=username,
        email=original_email,
        first_name=original_first_name,
        last_name=original_last_name,
        phone=TEST_PHONE,
        date_of_birth=datetime(1990, 1, 1).date(),
        marketing_emails_consent=True,
        password=TEST_PASSWORD,
        role=TEST_USER_ROLE
    )

    # Create a real User object for the return value
    updated_user = User(
        username=username,
        email=updated_email,
        first_name=updated_first_name,
        last_name=updated_last_name,
        phone=TEST_PHONE,
        date_of_birth=datetime(1990, 1, 1).date(),
        marketing_emails_consent=True,
        password=TEST_PASSWORD,
        role=TEST_USER_ROLE
    )

    # Mock user DAO
    mock_user_dao = MagicMock()
    mock_user_dao.get_user_by_email.return_value = None  # Email not in use
    mock_user_dao.update_user.return_value = updated_user

    # Test data
    update_data = UserProfileUpdateRequest(
        first_name=updated_first_name,
        last_name=updated_last_name,
        email=updated_email
    )

    # Call the function
    result = update_profile(
        update_data,
        request=create_mock_request(),
        current_user=mock_user,
        user_dao=mock_user_dao
    )

    # Verify result using local variables to avoid human error in assertions
    assert isinstance(result, ProfileResponse)
    assert result.user.first_name == updated_first_name
    assert result.user.last_name == updated_last_name
    assert result.user.email == updated_email


def test_update_profile_email_already_exists():
    """Test profile update with email already in use"""
    mock_user = MagicMock()
    mock_user.username = "john_doe"
    mock_user.email = "john@example.com"

    # Mock user DAO - email already exists
    mock_user_dao = MagicMock()
    mock_existing_user = MagicMock()
    mock_existing_user.username = "other_user"
    mock_user_dao.get_user_by_email.return_value = mock_existing_user

    # Test data
    update_data = UserProfileUpdateRequest(
        email="existing@example.com"  # Email already in use
    )

    # Call the function and expect exception
    with pytest.raises(CNOPUserAlreadyExistsException):
        update_profile(
            update_data,
            request=create_mock_request(),
            current_user=mock_user,
            user_dao=mock_user_dao
        )
        update_profile(
            update_data,
            request=create_mock_request(),
            current_user=mock_user,
            user_dao=mock_user_dao
        )