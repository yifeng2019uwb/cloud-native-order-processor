import pytest
from pydantic import ValidationError
from api_models.auth.profile import (
    UserProfileResponse,
    UserProfileUpdateRequest,
    ProfileUpdateSuccessResponse,
    ProfileUpdateErrorResponse
)
from datetime import datetime, date, timedelta
from user_exceptions import UserValidationException

# --- UserProfileResponse: Serialization with all fields ---
def test_user_profile_response_serialization():
    resp = UserProfileResponse(
        username="john_doe123",
        email="john.doe@example.com",
        first_name="John",
        last_name="Doe",
        phone="+1-555-123-4567",
        date_of_birth=date(1990, 5, 15),
        marketing_emails_consent=False,
        created_at=datetime(2025, 7, 9, 10, 30, 0),
        updated_at=datetime(2025, 7, 9, 10, 30, 0)
    )
    data = resp.model_dump()
    assert data["username"] == "john_doe123"
    assert data["email"] == "john.doe@example.com"
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert data["phone"] == "+1-555-123-4567"  # Response models don't sanitize
    assert data["date_of_birth"] == date(1990, 5, 15)
    assert data["marketing_emails_consent"] is False
    assert data["created_at"] == datetime(2025, 7, 9, 10, 30, 0)
    assert data["updated_at"] == datetime(2025, 7, 9, 10, 30, 0)

# --- UserProfileUpdateRequest: Valid update data ---
def test_user_profile_update_request_valid():
    req = UserProfileUpdateRequest(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="+1-555-123-4567",
        date_of_birth=date(1990, 5, 15)
    )
    assert req.first_name == "John"
    assert req.last_name == "Doe"
    assert req.email == "john.doe@example.com"
    assert req.phone == "15551234567"  # Sanitized to digits only
    assert req.date_of_birth == date(1990, 5, 15)

# --- First/last name validation ---
def test_user_profile_update_request_first_name_invalid():
    # Validation now happens at model level
    with pytest.raises(UserValidationException, match="Name must contain only letters, spaces, apostrophes, and hyphens"):
        UserProfileUpdateRequest(first_name="John1")
    with pytest.raises(UserValidationException, match="Name must contain only letters, spaces, apostrophes, and hyphens"):
        UserProfileUpdateRequest(first_name="J@hn")

def test_user_profile_update_request_last_name_invalid():
    # Validation now happens at model level
    with pytest.raises(UserValidationException, match="Name must contain only letters, spaces, apostrophes, and hyphens"):
        UserProfileUpdateRequest(last_name="Doe1")
    with pytest.raises(UserValidationException, match="Name must contain only letters, spaces, apostrophes, and hyphens"):
        UserProfileUpdateRequest(last_name="D0e")

def test_user_profile_update_request_first_last_name_valid():
    req = UserProfileUpdateRequest(first_name="John", last_name="Doe")
    assert req.first_name == "John"
    assert req.last_name == "Doe"

# --- Phone validation ---
def test_user_profile_update_request_phone_too_short():
    # Validation now happens at model level
    with pytest.raises(UserValidationException, match="Phone number must contain 10-15 digits"):
        UserProfileUpdateRequest(phone="12345")

def test_user_profile_update_request_phone_too_long():
    # Validation now happens at model level
    with pytest.raises(UserValidationException, match="Phone number must contain 10-15 digits"):
        UserProfileUpdateRequest(phone="1"*20)

def test_user_profile_update_request_phone_valid():
    req = UserProfileUpdateRequest(phone="(123) 456-7890")
    assert req.phone == "1234567890"  # Sanitized to digits only

# --- Date of birth validation ---
def test_user_profile_update_request_dob_in_future():
    # Validation now happens at model level
    future_date = date.today() + timedelta(days=1)
    with pytest.raises(UserValidationException, match="User must be at least 13 years old"):
        UserProfileUpdateRequest(date_of_birth=future_date)

def test_user_profile_update_request_dob_under_13():
    # Validation now happens at model level
    under_13 = date.today() - timedelta(days=12*365)
    with pytest.raises(UserValidationException, match="User must be at least 13 years old"):
        UserProfileUpdateRequest(date_of_birth=under_13)

def test_user_profile_update_request_dob_over_120():
    # Validation now happens at model level
    # Create a date that's exactly 121 years ago
    today = date.today()
    over_120 = date(today.year - 121, today.month, today.day)
    with pytest.raises(UserValidationException, match="Invalid date of birth"):
        UserProfileUpdateRequest(date_of_birth=over_120)

def test_user_profile_update_request_dob_valid():
    valid_dob = date.today() - timedelta(days=20*365)
    req = UserProfileUpdateRequest(date_of_birth=valid_dob)
    assert req.date_of_birth == valid_dob

# --- ProfileUpdateSuccessResponse serialization ---
def test_profile_update_success_response_serialization():
    user_info = UserProfileResponse(
        username="john_doe123",
        email="john.doe@example.com",
        first_name="John",
        last_name="Doe",
        phone="+1-555-123-4567",
        date_of_birth=date(1990, 5, 15),
        marketing_emails_consent=True,
        created_at=datetime(2025, 7, 9, 10, 30, 0),
        updated_at=datetime(2025, 7, 9, 10, 30, 0)
    )
    resp = ProfileUpdateSuccessResponse(
        success=True,
        message="Profile updated successfully",
        user=user_info
    )
    data = resp.model_dump()
    assert data["success"] is True
    assert data["message"] == "Profile updated successfully"
    assert data["user"]["username"] == "john_doe123"
    assert data["user"]["email"] == "john.doe@example.com"
    assert data["user"]["phone"] == "+1-555-123-4567"  # Response models don't sanitize
    assert data["user"]["created_at"] == datetime(2025, 7, 9, 10, 30, 0)
    assert data["user"]["updated_at"] == datetime(2025, 7, 9, 10, 30, 0)

# --- ProfileUpdateErrorResponse serialization ---
def test_profile_update_error_response_serialization():
    resp = ProfileUpdateErrorResponse(
        success=False,
        error="PROFILE_UPDATE_FAILED",
        message="Failed to update profile. Please try again.",
        details=None
    )
    data = resp.model_dump()
    assert data["success"] is False
    assert data["error"] == "PROFILE_UPDATE_FAILED"
    assert data["message"] == "Failed to update profile. Please try again."
    assert data["details"] is None
