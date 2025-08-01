import pytest
from pydantic import ValidationError
from api_models.auth.profile import (
    UserProfileResponse,
    UserProfileUpdateRequest,
    ProfileUpdateSuccessResponse,
    ProfileUpdateErrorResponse
)
from datetime import datetime, date, timedelta

# --- UserProfileResponse: Serialization with all fields ---
def test_user_profile_response_serialization():
    resp = UserProfileResponse(
        username="john_doe123",
        email="john.doe@example.com",
        first_name="John",
        last_name="Doe",
        phone="+1-555-123-4567",
        date_of_birth=date(1990, 5, 15),
        marketing_emails_consent=False
    )
    data = resp.model_dump()
    assert data["username"] == "john_doe123"
    assert data["email"] == "john.doe@example.com"
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert data["phone"] == "+1-555-123-4567"
    assert data["date_of_birth"] == date(1990, 5, 15)
    assert data["marketing_emails_consent"] is False

# --- UserProfileUpdateRequest: Valid update data ---
def test_user_profile_update_request_valid():
    req = UserProfileUpdateRequest(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="+1-555-123-4567",
        date_of_birth=date(1990, 5, 15),
        marketing_emails_consent=True
    )
    assert req.first_name == "John"
    assert req.last_name == "Doe"
    assert req.email == "john.doe@example.com"
    assert req.phone == "+1-555-123-4567"
    assert req.date_of_birth == date(1990, 5, 15)
    assert req.marketing_emails_consent is True

# --- First/last name validation ---
def test_user_profile_update_request_first_name_invalid():
    # Validation now happens in controller, not in API model
    req = UserProfileUpdateRequest(first_name="John1")
    assert req.first_name == "John1"
    req = UserProfileUpdateRequest(first_name="J@hn")
    assert req.first_name == "J@hn"

def test_user_profile_update_request_last_name_invalid():
    # Validation now happens in controller, not in API model
    req = UserProfileUpdateRequest(last_name="Doe1")
    assert req.last_name == "Doe1"
    req = UserProfileUpdateRequest(last_name="D0e")
    assert req.last_name == "D0e"

def test_user_profile_update_request_first_last_name_valid():
    req = UserProfileUpdateRequest(first_name="John", last_name="Doe")
    assert req.first_name == "John"
    assert req.last_name == "Doe"

# --- Phone validation ---
def test_user_profile_update_request_phone_too_short():
    # Validation now happens in controller, not in API model
    req = UserProfileUpdateRequest(phone="12345")
    assert req.phone == "12345"

def test_user_profile_update_request_phone_too_long():
    # Validation now happens in controller, not in API model
    req = UserProfileUpdateRequest(phone="1"*20)
    assert req.phone == "1"*20

def test_user_profile_update_request_phone_valid():
    req = UserProfileUpdateRequest(phone="(123) 456-7890")
    assert req.phone == "(123) 456-7890"

# --- Date of birth validation ---
def test_user_profile_update_request_dob_in_future():
    # Validation now happens in controller, not in API model
    future_date = date.today() + timedelta(days=1)
    req = UserProfileUpdateRequest(date_of_birth=future_date)
    assert req.date_of_birth == future_date

def test_user_profile_update_request_dob_under_13():
    # Validation now happens in controller, not in API model
    under_13 = date.today() - timedelta(days=12*365)
    req = UserProfileUpdateRequest(date_of_birth=under_13)
    assert req.date_of_birth == under_13

def test_user_profile_update_request_dob_over_120():
    # Validation now happens in controller, not in API model
    over_120 = date.today() - timedelta(days=121*365)
    req = UserProfileUpdateRequest(date_of_birth=over_120)
    assert req.date_of_birth == over_120

def test_user_profile_update_request_dob_valid():
    valid_dob = date.today() - timedelta(days=20*365)
    req = UserProfileUpdateRequest(date_of_birth=valid_dob)
    assert req.date_of_birth == valid_dob

# --- ProfileUpdateSuccessResponse serialization ---
def test_profile_update_success_response_serialization():
    user_profile = UserProfileResponse(
        username="john_doe123",
        email="john.smith@example.com",
        first_name="John",
        last_name="Smith",
        phone="+1-555-987-6543",
        date_of_birth=date(1990, 5, 15),
        marketing_emails_consent=True
    )
    resp = ProfileUpdateSuccessResponse(
        message="Profile updated successfully",
        user=user_profile
    )
    data = resp.model_dump()
    assert data["message"] == "Profile updated successfully"
    assert data["user"]["username"] == "john_doe123"
    assert data["user"]["email"] == "john.smith@example.com"
    assert data["user"]["first_name"] == "John"
    assert data["user"]["last_name"] == "Smith"
    assert data["user"]["phone"] == "+1-555-987-6543"
    assert data["user"]["date_of_birth"] == date(1990, 5, 15)
    assert data["user"]["marketing_emails_consent"] is True

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
