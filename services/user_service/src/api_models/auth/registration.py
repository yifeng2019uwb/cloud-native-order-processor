"""
Pydantic models specific to user registration API
"""
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional
from datetime import date

# Import centralized field validation functions
from validation.field_validators import (
    validate_username, validate_name, validate_email,
    validate_phone, validate_password, validate_date_of_birth
)

USERNAME_FIELD = "username"
EMAIL_FIELD = "email"
PASSWORD_FIELD = "password"
FIRST_NAME_FIELD = "first_name"
LAST_NAME_FIELD = "last_name"
PHONE_FIELD = "phone"
DATE_OF_BIRTH_FIELD = "date_of_birth"
MARKETING_EMAILS_CONSENT_FIELD = "marketing_emails_consent"

class UserRegistrationRequest(BaseModel):
    """Request model for POST /auth/register"""
    username: str = Field(..., min_length=6, max_length=30, description="Username")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=12, max_length=20, description="Password")
    first_name: str = Field(..., min_length=1, max_length=50, description="First name")
    last_name: str = Field(..., min_length=1, max_length=50, description="Last name")
    phone: Optional[str] = Field(None, description="Phone number")
    date_of_birth: Optional[date] = Field(None, description="Date of birth")
    marketing_emails_consent: bool = Field(default=False, description="Marketing emails consent")

    @field_validator(USERNAME_FIELD)
    @classmethod
    def validate_username_format(cls, v: str) -> str:
        """Layer 1: Basic format validation for username"""
        return validate_username(v)

    @field_validator(EMAIL_FIELD)
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        """Layer 1: Basic format validation for email"""
        return validate_email(v)

    @field_validator(PASSWORD_FIELD)
    @classmethod
    def validate_password_format(cls, v: str) -> str:
        """Layer 1: Basic format validation for password"""
        return validate_password(v)

    @field_validator(FIRST_NAME_FIELD)
    @classmethod
    def validate_first_name_format(cls, v: str) -> str:
        """Layer 1: Basic format validation for first name"""
        return validate_name(v)

    @field_validator(LAST_NAME_FIELD)
    @classmethod
    def validate_last_name_format(cls, v: str) -> str:
        """Layer 1: Basic format validation for last name"""
        return validate_name(v)

    @field_validator(PHONE_FIELD)
    @classmethod
    def validate_phone_format(cls, v: Optional[str]) -> Optional[str]:
        """Layer 1: Basic format validation for phone"""
        if v is None:
            return v
        return validate_phone(v)

    @field_validator(DATE_OF_BIRTH_FIELD)
    @classmethod
    def validate_date_of_birth_format(cls, v: Optional[date]) -> Optional[date]:
        """Layer 1: Basic format validation for date of birth"""
        if v is None:
            return v
        return validate_date_of_birth(v)


class RegistrationResponse(BaseModel):
    """Response model for successful user registration"""
    message: str = "User registered successfully"