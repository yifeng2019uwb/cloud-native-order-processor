"""
Tests for profile API models - Focus on field validation
"""
import pytest
from pydantic import ValidationError
from api_models.auth.profile import (
    UserProfileResponse,
    UserProfileUpdateRequest,
    ProfileResponse
)
from datetime import datetime, date, timedelta
from user_exceptions import CNOPUserValidationException

# Test constants
TEST_USERNAME = "john_doe123"
TEST_EMAIL = "john.doe@example.com"
TEST_FIRST_NAME = "John"
TEST_LAST_NAME = "Doe"
TEST_PHONE = "+1-555-123-4567"
TEST_DATE_OF_BIRTH = date(1990, 5, 15)
TEST_MARKETING_CONSENT = True
TEST_CREATED_AT = datetime(2025, 7, 9, 10, 30, 0)
TEST_UPDATED_AT = datetime(2025, 7, 9, 10, 30, 0)


def test_user_profile_response_valid():
    """Test valid UserProfileResponse creation"""
    profile = UserProfileResponse(
        username=TEST_USERNAME,
        email=TEST_EMAIL,
        first_name=TEST_FIRST_NAME,
        last_name=TEST_LAST_NAME,
        phone=TEST_PHONE,
        date_of_birth=TEST_DATE_OF_BIRTH,
        marketing_emails_consent=TEST_MARKETING_CONSENT,
        created_at=TEST_CREATED_AT,
        updated_at=TEST_UPDATED_AT
    )
    assert profile.username == TEST_USERNAME
    assert profile.email == TEST_EMAIL
    assert profile.first_name == TEST_FIRST_NAME
    assert profile.last_name == TEST_LAST_NAME


def test_user_profile_response_missing_required_fields():
    """Test UserProfileResponse with missing required fields"""
    with pytest.raises(ValidationError):
        UserProfileResponse()  # Missing all required fields


def test_user_profile_response_invalid_email():
    """Test UserProfileResponse with invalid email format"""
    with pytest.raises(ValidationError):
        UserProfileResponse(
            username=TEST_USERNAME,
            email="invalid-email",  # Invalid email format
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
            created_at=TEST_CREATED_AT,
            updated_at=TEST_UPDATED_AT
        )


def test_user_profile_update_request_valid():
    """Test valid UserProfileUpdateRequest creation"""
    request = UserProfileUpdateRequest(
        first_name=TEST_FIRST_NAME,
        last_name=TEST_LAST_NAME,
        email=TEST_EMAIL,
        phone=TEST_PHONE,
        date_of_birth=TEST_DATE_OF_BIRTH
    )
    assert request.first_name == TEST_FIRST_NAME
    assert request.last_name == TEST_LAST_NAME
    assert request.email == TEST_EMAIL


def test_user_profile_update_request_invalid_email():
    """Test UserProfileUpdateRequest with invalid email format"""
    with pytest.raises(ValidationError):
        UserProfileUpdateRequest(
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
            email="invalid-email",  # Invalid email format
            phone=TEST_PHONE,
            date_of_birth=TEST_DATE_OF_BIRTH
        )


def test_user_profile_update_request_invalid_date_of_birth():
    """Test UserProfileUpdateRequest with invalid date of birth"""
    # Future date - this will raise CNOPUserValidationException from field validator
    future_date = date.today() + timedelta(days=1)
    with pytest.raises(CNOPUserValidationException):
        UserProfileUpdateRequest(
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
            email=TEST_EMAIL,
            phone=TEST_PHONE,
            date_of_birth=future_date
        )


def test_profile_response_valid():
    """Test valid ProfileResponse creation"""
    user_profile = UserProfileResponse(
        username=TEST_USERNAME,
        email=TEST_EMAIL,
        first_name=TEST_FIRST_NAME,
        last_name=TEST_LAST_NAME,
        marketing_emails_consent=TEST_MARKETING_CONSENT,
        created_at=TEST_CREATED_AT,
        updated_at=TEST_UPDATED_AT
    )
    response = ProfileResponse(user=user_profile)
    assert response.user.username == TEST_USERNAME
    assert response.user.email == TEST_EMAIL