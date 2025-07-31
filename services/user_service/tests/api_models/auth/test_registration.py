"""
Tests for user registration request models
"""

import pytest
from datetime import date
from pydantic import ValidationError
from src.api_models.auth.registration import (
    UserRegistrationRequest,
    UserRegistrationResponse,
    RegistrationSuccessResponse,
    RegistrationErrorResponse
)


def test_valid_registration_data():
    req = UserRegistrationRequest(
        username="john_doe123",
        email="john.doe@example.com",
        password="SecurePassword123!",
        first_name="John",
        last_name="Doe",
        phone="+1-555-123-4567",
        date_of_birth=date(1990, 5, 15),
        marketing_emails_consent=True
    )
    assert req.username == "john_doe123"
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
    # Username with special chars - sanitization removes them
    req = UserRegistrationRequest(
        username="john<doe>123",
        email="test@example.com",
        password="SecurePassword123!",
        first_name="John",
        last_name="Doe"
    )
    # Sanitization removes < and > characters
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
    # First name with non-letters - basic sanitization only removes HTML tags
    req = UserRegistrationRequest(
        username="johndoe",
        email="test@example.com",
        password="SecurePassword123!",
        first_name="John123",
        last_name="Doe"
    )
    # Basic sanitization keeps numbers (only removes HTML tags)
    assert req.first_name == "John123"


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
    # Last name with non-letters - basic sanitization only removes HTML tags
    req = UserRegistrationRequest(
        username="johndoe",
        email="test@example.com",
        password="SecurePassword123!",
        first_name="John",
        last_name="Doe123"
    )
    # Basic sanitization keeps numbers (only removes HTML tags)
    assert req.last_name == "Doe123"


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
    with pytest.raises(ValidationError):
        UserRegistrationRequest(
            username="johndoe",
            email="test@example.com",
            password="SecurePassword123!",
            first_name="John",
            last_name="Doe",
            phone="123"  # Too short
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


def test_user_registration_response_serialization():
    from datetime import datetime
    resp = UserRegistrationResponse(
        username="john_doe123",
        email="john.doe@example.com",
        first_name="John",
        last_name="Doe",
        marketing_emails_consent=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    data = resp.model_dump()
    assert data["username"] == "john_doe123"
    assert data["email"] == "john.doe@example.com"
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert data["marketing_emails_consent"] is False


def test_registration_success_response_serialization():
    resp = RegistrationSuccessResponse(
        message="User registered successfully"
    )
    data = resp.model_dump()
    assert data["message"] == "User registered successfully"
    assert data["success"] is True


def test_registration_error_response_serialization():
    resp = RegistrationErrorResponse(
        error="REGISTRATION_FAILED",
        message="Registration failed"
    )
    data = resp.model_dump()
    assert data["message"] == "Registration failed"
    assert data["error"] == "REGISTRATION_FAILED"
    assert data["success"] is False
