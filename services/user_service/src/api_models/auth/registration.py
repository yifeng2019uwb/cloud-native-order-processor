"""
Pydantic models specific to user registration API
Path: cloud-native-order-processor/services/user-service/src/models/register_models.py
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import date
import re

from common.validators import sanitized_username, sanitized_email, sanitized_phone
from ..shared.common import UserBaseInfo, SuccessResponse, ErrorResponse


class UserRegistrationRequest(BaseModel):
    """Request model for POST /auth/register - Required + Optional Fields"""

    # Required Fields
    username: str = Field(
        ...,
        min_length=6,
        max_length=30,
        strip_whitespace=True,
        description="Unique username (6-30 characters, alphanumeric and underscores only)",  # UPDATED
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
        description="User password (12-20 characters with complexity requirements) - Examples show format only, not actual passwords",  # UPDATED
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
        description="Phone number (10-15 digits, optional)",  # UPDATED: removed length constraint
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
    def validate_username_format(cls, v):
        """Simple username validation with sanitization"""
        return sanitized_username()(v)

    @field_validator('password')
    @classmethod
    def validate_password_complexity(cls, v):
        """Password complexity validation"""
        if len(v) < 12:
            raise ValueError("Password must be at least 12 characters long")

        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")

        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")

        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")

        if not re.search(r"[!@#$%^&*()\-_=+]", v):
            raise ValueError("Password must contain at least one special character (!@#$%^&*()-_=+)")

        return v

    @field_validator('first_name')
    @classmethod
    def validate_first_name_format(cls, v):
        """Simple first name validation with sanitization"""
        from common.validators import sanitized_string
        return sanitized_string(max_length=50)(v)

    @field_validator('last_name')
    @classmethod
    def validate_last_name_format(cls, v):
        """Simple last name validation with sanitization"""
        from common.validators import sanitized_string
        return sanitized_string(max_length=50)(v)

    @field_validator('phone')
    @classmethod
    def validate_phone_format(cls, v):
        """Simple phone validation with sanitization"""
        return sanitized_phone()(v)

    @field_validator('date_of_birth')
    @classmethod
    def validate_age_requirements(cls, v):
        """Simple date of birth validation with age requirements"""
        if v is None:
            return v

        from datetime import date, timedelta
        today = date.today()

        # Check if date is in the future
        if v > today:
            raise ValueError('Date of birth cannot be in the future')

        # Check minimum age (13 years for COPPA compliance)
        min_age_date = today - timedelta(days=13 * 365.25)
        if v > min_age_date:
            raise ValueError('Must be at least 13 years old to register')

        # Check maximum reasonable age (120 years)
        max_age_date = today - timedelta(days=120 * 365.25)
        if v < max_age_date:
            raise ValueError('Invalid date of birth')

        return v

    class Config:
        """Pydantic model configuration"""
        json_schema_extra = {
            "example": {
                "username": "john_doe123",
                "email": "john.doe@example.com",
                "password": "SecurePassword123!",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+1-555-123-4567",
                "date_of_birth": "1990-05-15",
                "marketing_emails_consent": False
            }
        }


class UserRegistrationResponse(UserBaseInfo):
    """Response model for successful user registration"""

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe123",
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+1-555-123-4567",
                "date_of_birth": "1990-05-15",
                "marketing_emails_consent": False,
                "created_at": "2025-07-09T10:30:00Z",
                "updated_at": "2025-07-09T10:30:00Z"
            }
        }


class RegistrationSuccessResponse(SuccessResponse):
    """Success response wrapper for registration - simple success message only

    Design Decision: Registration returns minimal response (no token/user data)
    - Registration = Account creation only
    - Login = Authentication + basic user data
    - Profile = Full user details

    Future Enhancement: Email verification will be added between registration and login
    """
    message: str = Field(
        default="Account created successfully. Please login to continue.",
        description="Registration success message"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Account created successfully. Please login to continue.",
                "timestamp": "2025-07-09T10:30:00Z"
            }
        }


class RegistrationErrorResponse(ErrorResponse):
    """Error response specific to registration failures"""

    error: str = Field(
        ...,
        description="Registration error code",
        example="REGISTRATION_FAILED"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "REGISTRATION_FAILED",
                "message": "Unable to create account. Please try again or contact support.",
                "details": None,
                "timestamp": "2025-07-09T10:30:00Z"
            }
        }