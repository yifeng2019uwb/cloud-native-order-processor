"""
Pydantic models specific to user registration API
Path: cloud-native-order-processor/services/user-service/src/models/register_models.py

Layer 1: Model validation (field format, basic sanitization)
Layer 2: Business validation (in service layer)
"""
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional
from datetime import date

from ..shared.common import UserBaseInfo, SuccessResponse, ErrorResponse

# Import centralized field validation functions
from validation.field_validators import (
    validate_username, validate_name, validate_email,
    validate_phone, validate_password, validate_date_of_birth
)

# Import custom exceptions
from common.exceptions.shared_exceptions import UserValidationException


class UserRegistrationRequest(BaseModel):
    """
    Request model for POST /auth/register - Required + Optional Fields

    Layer 1 Validation: Field format, basic sanitization
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "john_doe123",
                "email": "john.doe@example.com",
                "password": "SecurePassword123!",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+1-555-123-4567",
                "date_of_birth": "1990-05-15",
                "marketing_emails_consent": True
            }
        }
    )

    # Required Fields
    username: str = Field(
        ...,
        min_length=6,
        max_length=30,
        strip_whitespace=True,
        description="Unique username (6-30 characters, alphanumeric and underscores only)",
        example="john_doe123"
    )

    email: EmailStr = Field(
        ...,
        description="Unique email address (must be valid email format)",
        example="john.doe@example.com"
    )

    password: str = Field(
        ...,
        min_length=12,
        max_length=20,
        description="User password (12-20 characters with complexity requirements)",
        example="SecurePassword123!"
    )

    first_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        strip_whitespace=True,
        description="User first name (1-50 characters)",
        example="John"
    )

    last_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        strip_whitespace=True,
        description="User last name (1-50 characters)",
        example="Doe"
    )

    # Optional Fields
    phone: Optional[str] = Field(
        None,
        description="Phone number (10-15 digits, optional)",
        example="+1-555-123-4567"
    )

    date_of_birth: Optional[date] = Field(
        None,
        description="Date of birth (YYYY-MM-DD format, optional)",
        example="1990-05-15"
    )

    marketing_emails_consent: bool = Field(
        default=False,
        description="Consent to receive marketing emails (GDPR compliance)"
    )

    @field_validator('username')
    @classmethod
    def validate_username_format(cls, v: str) -> str:
        """Layer 1: Basic format validation for username"""
        return validate_username(v)

    @field_validator('email')
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        """Layer 1: Basic format validation for email"""
        return validate_email(v)

    @field_validator('password')
    @classmethod
    def validate_password_format(cls, v: str) -> str:
        """Layer 1: Basic format validation for password"""
        return validate_password(v)

    @field_validator('first_name')
    @classmethod
    def validate_first_name_format(cls, v: str) -> str:
        """Layer 1: Basic format validation for first name"""
        return validate_name(v)

    @field_validator('last_name')
    @classmethod
    def validate_last_name_format(cls, v: str) -> str:
        """Layer 1: Basic format validation for last name"""
        return validate_name(v)

    @field_validator('phone')
    @classmethod
    def validate_phone_format(cls, v: Optional[str]) -> Optional[str]:
        """Layer 1: Basic format validation for phone"""
        if v is None:
            return v
        return validate_phone(v)

    @field_validator('date_of_birth')
    @classmethod
    def validate_date_of_birth_format(cls, v: Optional[date]) -> Optional[date]:
        """Layer 1: Basic format validation for date of birth"""
        if v is None:
            return v
        return validate_date_of_birth(v)


# --- Registration Success Response ---
class RegistrationSuccessResponse(SuccessResponse):
    """Success response wrapper for user registration"""

    message: str = Field(
        default="User registered successfully",
        description="Registration success message"
    )

    # TODO: Add email confirmation functionality later
    # For now, just return success - user can login immediately
    # Future enhancement: Send confirmation email and require verification

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "User registered successfully",
                "data": None,
                "timestamp": "2025-07-09T10:30:00Z"
            }
        }
    )


# --- Registration Error Response ---
class RegistrationErrorResponse(ErrorResponse):
    """Error response specific to registration failures"""

    error: str = Field(
        default="REGISTRATION_FAILED",
        description="Registration error code"
    )

    message: str = Field(
        default="Registration failed. Please check your information and try again.",
        description="Registration error message"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": False,
                "error": "REGISTRATION_FAILED",
                "message": "Registration failed. Please check your information and try again.",
                "details": None,
                "timestamp": "2025-07-09T10:30:00Z"
            }
        }
    )