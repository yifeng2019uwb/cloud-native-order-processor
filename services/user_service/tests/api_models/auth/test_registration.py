"""
Tests for user registration request models
"""

import pytest
from datetime import date, timedelta
from pydantic import ValidationError
from api_models.auth.registration import (
    UserRegistrationRequest,
    RegistrationSuccessResponse,
    RegistrationErrorResponse
)
from api_models.shared.common import ErrorResponse
from exceptions import UserValidationException


def test_valid_registration_data():
    # Valid registration data
    req = UserRegistrationRequest(
        username="johndoe",
        email="john.doe@example.com",
        password="SecurePassword123!",
        first_name="John",
        last_name="Doe",
        phone="+1-555-123-4567",
        date_of_birth=date(1990, 5, 15),
        marketing_emails_consent=True
    )
    assert req.username == "johndoe"
    assert req.email == "john.doe@example.com"
    assert req.password == "SecurePassword123!"
    assert req.first_name == "John"
    assert req.last_name == "Doe"
    # Phone is sanitized to digits only
    assert req.phone == "15551234567"
    assert req.date_of_birth == date(1990, 5, 15)
    assert req.marketing_emails_consent is True


def test_username_validation():
    # Valid username
    req = UserRegistrationRequest(
        username="john_doe123",
        email="test@example.com",
        password="SecurePassword123!",
        first_name="John",
        last_name="Doe"
    )
    assert req.username == "john_doe123"


def test_username_invalid_characters():
    # Username with special chars - sanitized to remove HTML tags
    req = UserRegistrationRequest(
        username="john<doe>123",
        email="test@example.com",
        password="SecurePassword123!",
        first_name="John",
        last_name="Doe"
    )
    # HTML tags are removed during sanitization
    assert req.username == "john123"


def test_username_starts_or_ends_with_underscore():
    # Username with underscores - sanitization allows them
    req = UserRegistrationRequest(
        username="_john_doe_",
        email="test@example.com",
        password="SecurePassword123!",
        first_name="John",
        last_name="Doe"
    )
    # Sanitization allows underscores
    assert req.username == "_john_doe_"


def test_username_consecutive_underscores():
    # Username with consecutive underscores - sanitization allows them
    req = UserRegistrationRequest(
        username="john__doe",
        email="test@example.com",
        password="SecurePassword123!",
        first_name="John",
        last_name="Doe"
    )
    # Sanitization allows consecutive underscores
    assert req.username == "john__doe"


def test_username_too_short():
    with pytest.raises(ValidationError):
        UserRegistrationRequest(
            username="ab",  # Too short
            email="test@example.com",
            password="SecurePassword123!",
            first_name="John",
            last_name="Doe"
        )


def test_username_too_long():
    with pytest.raises(ValidationError):
        UserRegistrationRequest(
            username="a" * 31,  # Too long
            email="test@example.com",
            password="SecurePassword123!",
            first_name="John",
            last_name="Doe"
        )


def test_email_validation():
    # Valid email
    req = UserRegistrationRequest(
        username="johndoe",
        email="john.doe@example.com",
        password="SecurePassword123!",
        first_name="John",
        last_name="Doe"
    )
    assert req.email == "john.doe@example.com"


def test_email_invalid_format():
    with pytest.raises(ValidationError):
        UserRegistrationRequest(
            username="johndoe",
            email="invalid-email",
            password="SecurePassword123!",
            first_name="John",
            last_name="Doe"
        )


def test_password_validation():
    # Valid password
    req = UserRegistrationRequest(
        username="johndoe",
        email="test@example.com",
        password="SecurePassword123!",
        first_name="John",
        last_name="Doe"
    )
    assert req.password == "SecurePassword123!"


def test_password_too_short():
    with pytest.raises(ValidationError):
        UserRegistrationRequest(
            username="johndoe",
            email="test@example.com",
            password="short",  # Too short
            first_name="John",
            last_name="Doe"
        )


def test_first_name_validation():
    # Valid first name
    req = UserRegistrationRequest(
        username="johndoe",
        email="test@example.com",
        password="SecurePassword123!",
        first_name="John",
        last_name="Doe"
    )
    assert req.first_name == "John"


def test_first_name_non_letters():
    # First name with non-letters - validation now happens at model level
    with pytest.raises(UserValidationException, match="Name must contain only letters, spaces, apostrophes, and hyphens"):
        UserRegistrationRequest(
            username="johndoe",
            email="test@example.com",
            password="SecurePassword123!",
            first_name="John1",
            last_name="Doe"
        )


def test_last_name_validation():
    # Valid last name
    req = UserRegistrationRequest(
        username="johndoe",
        email="test@example.com",
        password="SecurePassword123!",
        first_name="John",
        last_name="Doe"
    )
    assert req.last_name == "Doe"


def test_last_name_non_letters():
    # Last name with non-letters - validation now happens at model level
    with pytest.raises(UserValidationException, match="Name must contain only letters, spaces, apostrophes, and hyphens"):
        UserRegistrationRequest(
            username="johndoe",
            email="test@example.com",
            password="SecurePassword123!",
            first_name="John",
            last_name="Doe123"
        )


def test_phone_validation():
    # Valid phone
    req = UserRegistrationRequest(
        username="johndoe",
        email="test@example.com",
        password="SecurePassword123!",
        first_name="John",
        last_name="Doe",
        phone="+1-555-123-4567"
    )
    # Phone is sanitized to digits only
    assert req.phone == "15551234567"


def test_phone_valid_formats():
    req = UserRegistrationRequest(
        username="johndoe",
        email="a@b.com",
        password="SecurePassword123!",
        first_name="John",
        last_name="Doe",
        phone="(123) 456-7890"
    )
    # Phone is sanitized to digits only
    assert req.phone == "1234567890"


def test_phone_invalid_format():
    # Phone validation now happens at model level
    with pytest.raises(UserValidationException, match="Phone number must contain 10-15 digits"):
        UserRegistrationRequest(
            username="johndoe",
            email="test@example.com",
            password="SecurePassword123!",
            first_name="John",
            last_name="Doe",
            phone="123"  # Too short - will be rejected at model level
        )


def test_date_of_birth_validation():
    # Valid date of birth
    req = UserRegistrationRequest(
        username="johndoe",
        email="test@example.com",
        password="SecurePassword123!",
        first_name="John",
        last_name="Doe",
        date_of_birth=date(1990, 5, 15)
    )
    assert req.date_of_birth == date(1990, 5, 15)


def test_date_of_birth_future():
    # Future date validation now happens at model level
    future_date = date.today() + timedelta(days=1)
    with pytest.raises(UserValidationException, match="User must be at least 13 years old"):
        UserRegistrationRequest(
            username="johndoe",
            email="test@example.com",
            password="SecurePassword123!",
            first_name="John",
            last_name="Doe",
            date_of_birth=future_date  # Future date - will be rejected at model level
        )


def test_date_of_birth_under_13():
    # Under 13 validation now happens at model level
    under_13 = date.today() - timedelta(days=12*365)
    with pytest.raises(UserValidationException, match="User must be at least 13 years old"):
        UserRegistrationRequest(
            username="johndoe",
            email="test@example.com",
            password="SecurePassword123!",
            first_name="John",
            last_name="Doe",
            date_of_birth=under_13  # Under 13 - will be rejected at model level
        )


def test_marketing_emails_consent():
    # With consent
    req = UserRegistrationRequest(
        username="johndoe",
        email="test@example.com",
        password="SecurePassword123!",
        first_name="John",
        last_name="Doe",
        marketing_emails_consent=True
    )
    assert req.marketing_emails_consent is True

    # Without consent
    req = UserRegistrationRequest(
        username="johndoe",
        email="test@example.com",
        password="SecurePassword123!",
        first_name="John",
        last_name="Doe",
        marketing_emails_consent=False
    )
    assert req.marketing_emails_consent is False


def test_optional_fields():
    # Without optional fields
    req = UserRegistrationRequest(
        username="johndoe",
        email="test@example.com",
        password="SecurePassword123!",
        first_name="John",
        last_name="Doe"
    )
    assert req.phone is None
    assert req.date_of_birth is None
    assert req.marketing_emails_consent is False


# --- RegistrationSuccessResponse serialization ---
def test_registration_success_response_serialization():
    resp = RegistrationSuccessResponse(
        message="User registered successfully"
    )
    data = resp.model_dump()
    assert data["success"] is True
    assert data["message"] == "User registered successfully"
    assert data["data"] is None


def test_registration_error_response_serialization():
    resp = RegistrationErrorResponse(
        error="REGISTRATION_FAILED",
        message="Registration failed"
    )
    data = resp.model_dump()
    assert data["message"] == "Registration failed"
    assert data["error"] == "REGISTRATION_FAILED"
    assert data["success"] is False
