"""
Tests for registration API models - Focus on field validation
"""
import pytest
from datetime import date, timedelta
from pydantic import ValidationError
from api_models.auth.registration import (
    UserRegistrationRequest,
    RegistrationResponse
)
from user_exceptions import CNOPUserValidationException

# Test constants
TEST_USERNAME = "john_doe123"
TEST_EMAIL = "john.doe@example.com"
TEST_PASSWORD = "SecurePassword123!"
TEST_FIRST_NAME = "John"
TEST_LAST_NAME = "Doe"
TEST_PHONE = "+1-555-123-4567"
TEST_DATE_OF_BIRTH = date(1990, 5, 15)
TEST_MARKETING_CONSENT = True


def test_user_registration_request_valid():
    """Test valid UserRegistrationRequest creation"""
    request = UserRegistrationRequest(
        username=TEST_USERNAME,
        email=TEST_EMAIL,
        password=TEST_PASSWORD,
        first_name=TEST_FIRST_NAME,
        last_name=TEST_LAST_NAME,
        phone=TEST_PHONE,
        date_of_birth=TEST_DATE_OF_BIRTH,
        marketing_emails_consent=TEST_MARKETING_CONSENT
    )
    assert request.username == TEST_USERNAME
    assert request.email == TEST_EMAIL
    assert request.password == TEST_PASSWORD
    assert request.first_name == TEST_FIRST_NAME
    assert request.last_name == TEST_LAST_NAME


def test_user_registration_request_missing_required_fields():
    """Test UserRegistrationRequest with missing required fields"""
    with pytest.raises(ValidationError):
        UserRegistrationRequest()  # Missing all required fields

    with pytest.raises(ValidationError):
        UserRegistrationRequest(username=TEST_USERNAME)  # Missing other required fields


def test_user_registration_request_username_validation():
    """Test username field validation"""
    # Too short
    with pytest.raises(ValidationError):
        UserRegistrationRequest(
            username="ab",  # Too short
            email=TEST_EMAIL,
            password=TEST_PASSWORD,
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME
        )

    # Too long
    with pytest.raises(ValidationError):
        UserRegistrationRequest(
            username="a" * 31,  # Too long
            email=TEST_EMAIL,
            password=TEST_PASSWORD,
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME
        )


def test_user_registration_request_email_validation():
    """Test email field validation"""
    with pytest.raises(ValidationError):
        UserRegistrationRequest(
            username=TEST_USERNAME,
            email="invalid-email",  # Invalid email format
            password=TEST_PASSWORD,
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME
        )


def test_user_registration_request_password_validation():
    """Test password field validation"""
    # Too short
    with pytest.raises(ValidationError):
        UserRegistrationRequest(
            username=TEST_USERNAME,
            email=TEST_EMAIL,
            password="short",  # Too short
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME
        )

    # Too long
    with pytest.raises(ValidationError):
        UserRegistrationRequest(
            username=TEST_USERNAME,
            email=TEST_EMAIL,
            password="a" * 21,  # Too long
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME
        )


def test_user_registration_request_name_validation():
    """Test first_name and last_name field validation"""
    # Invalid first name
    with pytest.raises(CNOPUserValidationException):
        UserRegistrationRequest(
            username=TEST_USERNAME,
            email=TEST_EMAIL,
            password=TEST_PASSWORD,
            first_name="John1",  # Contains number
            last_name=TEST_LAST_NAME
        )

    # Invalid last name
    with pytest.raises(CNOPUserValidationException):
        UserRegistrationRequest(
            username=TEST_USERNAME,
            email=TEST_EMAIL,
            password=TEST_PASSWORD,
            first_name=TEST_FIRST_NAME,
            last_name="Doe@123"  # Contains special characters
        )


def test_user_registration_request_phone_validation():
    """Test phone field validation"""
    # Too short
    with pytest.raises(CNOPUserValidationException):
        UserRegistrationRequest(
            username=TEST_USERNAME,
            email=TEST_EMAIL,
            password=TEST_PASSWORD,
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
            phone="123"  # Too short
        )

    # Too long
    with pytest.raises(CNOPUserValidationException):
        UserRegistrationRequest(
            username=TEST_USERNAME,
            email=TEST_EMAIL,
            password=TEST_PASSWORD,
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
            phone="1" * 20  # Too long
        )


def test_user_registration_request_date_of_birth_validation():
    """Test date_of_birth field validation"""
    # Future date
    future_date = date.today() + timedelta(days=1)
    with pytest.raises(CNOPUserValidationException):
        UserRegistrationRequest(
            username=TEST_USERNAME,
            email=TEST_EMAIL,
            password=TEST_PASSWORD,
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
            date_of_birth=future_date
        )

    # Too young (under 13)
    under_13 = date.today() - timedelta(days=12*365)
    with pytest.raises(CNOPUserValidationException):
        UserRegistrationRequest(
            username=TEST_USERNAME,
            email=TEST_EMAIL,
            password=TEST_PASSWORD,
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
            date_of_birth=under_13
        )


def test_user_registration_request_optional_fields():
    """Test optional fields work correctly"""
    # Without optional fields
    request = UserRegistrationRequest(
        username=TEST_USERNAME,
        email=TEST_EMAIL,
        password=TEST_PASSWORD,
        first_name=TEST_FIRST_NAME,
        last_name=TEST_LAST_NAME
    )
    assert request.phone is None
    assert request.date_of_birth is None
    assert request.marketing_emails_consent is False


def test_registration_response_valid():
    """Test valid RegistrationResponse creation"""
    response = RegistrationResponse()
    assert response.message == "User registered successfully"


def test_registration_response_custom_message():
    """Test RegistrationResponse with custom message"""
    custom_message = "Custom registration message"
    response = RegistrationResponse(message=custom_message)
    assert response.message == custom_message