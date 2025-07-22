import pytest
from pydantic import ValidationError
from datetime import date, timedelta
from api_models.auth.registration import (
    UserRegistrationRequest,
    UserRegistrationResponse,
    RegistrationSuccessResponse,
    RegistrationErrorResponse
)

# --- UserRegistrationRequest: Valid registration data ---
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
    assert req.phone == "+1-555-123-4567"
    assert req.date_of_birth == date(1990, 5, 15)
    assert req.marketing_emails_consent is True

# --- Username validation ---
def test_username_too_short():
    with pytest.raises(ValidationError):
        UserRegistrationRequest(
            username="abc",
            email="a@b.com",
            password="SecurePassword123!",
            first_name="John",
            last_name="Doe"
        )

def test_username_too_long():
    with pytest.raises(ValidationError):
        UserRegistrationRequest(
            username="a"*31,
            email="a@b.com",
            password="SecurePassword123!",
            first_name="John",
            last_name="Doe"
        )

def test_username_invalid_characters():
    with pytest.raises(ValidationError):
        UserRegistrationRequest(
            username="john.doe!",
            email="a@b.com",
            password="SecurePassword123!",
            first_name="John",
            last_name="Doe"
        )

def test_username_starts_or_ends_with_underscore():
    with pytest.raises(ValidationError):
        UserRegistrationRequest(
            username="_johndoe",
            email="a@b.com",
            password="SecurePassword123!",
            first_name="John",
            last_name="Doe"
        )
    with pytest.raises(ValidationError):
        UserRegistrationRequest(
            username="johndoe_",
            email="a@b.com",
            password="SecurePassword123!",
            first_name="John",
            last_name="Doe"
        )

def test_username_consecutive_underscores():
    with pytest.raises(ValidationError):
        UserRegistrationRequest(
            username="john__doe",
            email="a@b.com",
            password="SecurePassword123!",
            first_name="John",
            last_name="Doe"
        )

# --- Password validation ---
def test_password_missing_uppercase():
    with pytest.raises(ValidationError):
        UserRegistrationRequest(
            username="johndoe123",
            email="a@b.com",
            password="securepassword123!",
            first_name="John",
            last_name="Doe"
        )

def test_password_missing_lowercase():
    with pytest.raises(ValidationError):
        UserRegistrationRequest(
            username="johndoe123",
            email="a@b.com",
            password="SECUREPASSWORD123!",
            first_name="John",
            last_name="Doe"
        )

def test_password_missing_digit():
    with pytest.raises(ValidationError):
        UserRegistrationRequest(
            username="johndoe123",
            email="a@b.com",
            password="SecurePassword!!!",
            first_name="John",
            last_name="Doe"
        )

def test_password_missing_special():
    with pytest.raises(ValidationError):
        UserRegistrationRequest(
            username="johndoe123",
            email="a@b.com",
            password="SecurePassword123",
            first_name="John",
            last_name="Doe"
        )

def test_password_too_short():
    with pytest.raises(ValidationError):
        UserRegistrationRequest(
            username="johndoe123",
            email="a@b.com",
            password="S1!a",
            first_name="John",
            last_name="Doe"
        )

def test_password_too_long():
    with pytest.raises(ValidationError):
        UserRegistrationRequest(
            username="johndoe123",
            email="a@b.com",
            password="A1!" + "a"*18,
            first_name="John",
            last_name="Doe"
        )

# --- First/last name validation ---
def test_first_name_non_letters():
    with pytest.raises(ValidationError):
        UserRegistrationRequest(
            username="johndoe123",
            email="a@b.com",
            password="SecurePassword123!",
            first_name="John1",
            last_name="Doe"
        )

def test_last_name_non_letters():
    with pytest.raises(ValidationError):
        UserRegistrationRequest(
            username="johndoe123",
            email="a@b.com",
            password="SecurePassword123!",
            first_name="John",
            last_name="Doe!"
        )

def test_first_name_too_short():
    with pytest.raises(ValidationError):
        UserRegistrationRequest(
            username="johndoe123",
            email="a@b.com",
            password="SecurePassword123!",
            first_name="",
            last_name="Doe"
        )

def test_first_name_too_long():
    with pytest.raises(ValidationError):
        UserRegistrationRequest(
            username="johndoe123",
            email="a@b.com",
            password="SecurePassword123!",
            first_name="A"*51,
            last_name="Doe"
        )

def test_last_name_too_short():
    with pytest.raises(ValidationError):
        UserRegistrationRequest(
            username="johndoe123",
            email="a@b.com",
            password="SecurePassword123!",
            first_name="John",
            last_name=""
        )

def test_last_name_too_long():
    with pytest.raises(ValidationError):
        UserRegistrationRequest(
            username="johndoe123",
            email="a@b.com",
            password="SecurePassword123!",
            first_name="John",
            last_name="A"*51
        )

# --- Phone validation ---
def test_phone_too_short():
    with pytest.raises(ValidationError):
        UserRegistrationRequest(
            username="johndoe123",
            email="a@b.com",
            password="SecurePassword123!",
            first_name="John",
            last_name="Doe",
            phone="12345"
        )

def test_phone_too_long():
    with pytest.raises(ValidationError):
        UserRegistrationRequest(
            username="johndoe123",
            email="a@b.com",
            password="SecurePassword123!",
            first_name="John",
            last_name="Doe",
            phone="1"*20
        )

def test_phone_valid_formats():
    req = UserRegistrationRequest(
        username="johndoe123",
        email="a@b.com",
        password="SecurePassword123!",
        first_name="John",
        last_name="Doe",
        phone="(123) 456-7890"
    )
    assert req.phone == "(123) 456-7890"

# --- Date of birth validation ---
def test_dob_in_future():
    future_date = date.today() + timedelta(days=1)
    with pytest.raises(ValidationError):
        UserRegistrationRequest(
            username="johndoe123",
            email="a@b.com",
            password="SecurePassword123!",
            first_name="John",
            last_name="Doe",
            date_of_birth=future_date
        )

def test_dob_under_13():
    under_13 = date.today() - timedelta(days=12*365)
    with pytest.raises(ValidationError):
        UserRegistrationRequest(
            username="johndoe123",
            email="a@b.com",
            password="SecurePassword123!",
            first_name="John",
            last_name="Doe",
            date_of_birth=under_13
        )

def test_dob_over_120():
    over_120 = date.today() - timedelta(days=121*365)
    with pytest.raises(ValidationError):
        UserRegistrationRequest(
            username="johndoe123",
            email="a@b.com",
            password="SecurePassword123!",
            first_name="John",
            last_name="Doe",
            date_of_birth=over_120
        )

def test_dob_valid():
    valid_dob = date.today() - timedelta(days=20*365)
    req = UserRegistrationRequest(
        username="johndoe123",
        email="a@b.com",
        password="SecurePassword123!",
        first_name="John",
        last_name="Doe",
        date_of_birth=valid_dob
    )
    assert req.date_of_birth == valid_dob

# --- Marketing emails consent ---
def test_marketing_emails_consent_default():
    req = UserRegistrationRequest(
        username="johndoe123",
        email="a@b.com",
        password="SecurePassword123!",
        first_name="John",
        last_name="Doe"
    )
    assert req.marketing_emails_consent is False

def test_marketing_emails_consent_explicit():
    req = UserRegistrationRequest(
        username="johndoe123",
        email="a@b.com",
        password="SecurePassword123!",
        first_name="John",
        last_name="Doe",
        marketing_emails_consent=True
    )
    assert req.marketing_emails_consent is True

# --- UserRegistrationResponse serialization ---
def test_user_registration_response_serialization():
    resp = UserRegistrationResponse(
        username="john_doe123",
        email="john.doe@example.com",
        first_name="John",
        last_name="Doe",
        phone="+1-555-123-4567",
        date_of_birth=date(1990, 5, 15),
        marketing_emails_consent=False,
        created_at="2025-07-09T10:30:00Z",
        updated_at="2025-07-09T10:30:00Z"
    )
    data = resp.dict()
    assert data["username"] == "john_doe123"
    assert data["email"] == "john.doe@example.com"
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert data["phone"] == "+1-555-123-4567"
    assert data["date_of_birth"] == date(1990, 5, 15)
    assert data["marketing_emails_consent"] is False
    assert "created_at" in data
    assert "updated_at" in data

# --- RegistrationSuccessResponse serialization ---
def test_registration_success_response_serialization():
    resp = RegistrationSuccessResponse(
        message="Account created successfully",
        access_token="token123",
        token_type="bearer",
        expires_in=86400,
        username="john_doe123",
        is_new_user=True
    )
    data = resp.dict()
    assert data["message"] == "Account created successfully"
    assert data["access_token"] == "token123"
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == 86400
    assert data["username"] == "john_doe123"
    assert data["is_new_user"] is True

# --- RegistrationErrorResponse serialization ---
def test_registration_error_response_serialization():
    resp = RegistrationErrorResponse(
        success=False,
        error="REGISTRATION_FAILED",
        message="Unable to create account. Please try again or contact support.",
        details=None
    )
    data = resp.dict()
    assert data["success"] is False
    assert data["error"] == "REGISTRATION_FAILED"
    assert data["message"] == "Unable to create account. Please try again or contact support."
    assert data["details"] is None
