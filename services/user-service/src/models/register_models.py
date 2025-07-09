"""
Pydantic models specific to user registration API
Path: cloud-native-order-processor/services/user-service/src/models/register_models.py
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import date
import re

from .shared_models import UserBaseInfo, SuccessResponse, ErrorResponse


class UserRegistrationRequest(BaseModel):
    """Request model for POST /auth/register - Required + Optional Fields"""

    # Required Fields
    username: str = Field(
        ...,
        min_length=3,
        max_length=30,
        strip_whitespace=True,
        description="Unique username (3-30 characters, alphanumeric and underscores only)",
        example="john_doe123"
    )

    email: EmailStr = Field(
        ...,
        description="Unique email address (must be valid email format)",
        example="john.doe@example.com"
    )

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User password (8-128 characters)",
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
        min_length=10,
        max_length=20,
        description="Phone number (international format, 10-20 characters, optional)",
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

    @validator('username')
    def validate_username_format(cls, v):
        """
        Validate username format:
        - Only alphanumeric characters and underscores
        - Cannot start or end with underscore
        - Cannot have consecutive underscores
        """
        if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9_]*[a-zA-Z0-9]$|^[a-zA-Z0-9]$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores. Cannot start/end with underscore.')

        if '__' in v:
            raise ValueError('Username cannot contain consecutive underscores')

        return v.lower()  # Store usernames in lowercase for consistency

    @validator('first_name')
    def validate_first_name_format(cls, v):
        """Validate first name contains only letters"""
        if not re.match(r"^[a-zA-Z]+$", v):
            raise ValueError('First name can only contain letters')
        return v.title()  # Convert to title case

    @validator('last_name')
    def validate_last_name_format(cls, v):
        """Validate last name contains only letters"""
        if not re.match(r"^[a-zA-Z]+$", v):
            raise ValueError('Last name can only contain letters')
        return v.title()  # Convert to title case

    @validator('phone')
    def validate_phone_format(cls, v):
        """
        Validate phone number format if provided
        - Must contain 10-15 digits after removing non-digit characters
        - Can include international formatting (+, -, spaces, parentheses)
        """
        if v is None:
            return v

        # Remove all non-digit characters to count digits
        digits_only = re.sub(r'\D', '', v)

        if len(digits_only) < 10:
            raise ValueError('Phone number must contain at least 10 digits')
        if len(digits_only) > 15:
            raise ValueError('Phone number must contain no more than 15 digits')

        return v

    @validator('date_of_birth')
    def validate_age_requirements(cls, v):
        """
        Validate date of birth meets age requirements
        - Must be at least 13 years old (COPPA compliance)
        - Cannot be in the future
        """
        if v is None:
            return v

        from datetime import date, timedelta
        today = date.today()

        # Check if date is in the future
        if v > today:
            raise ValueError('Date of birth cannot be in the future')

        # Check minimum age (13 years for COPPA compliance)
        min_age_date = today - timedelta(days=13 * 365.25)  # Approximate 13 years
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
    """Success response wrapper for registration"""

    message: str = Field(
        default="Account created successfully",
        description="Registration success message"
    )

    user: UserRegistrationResponse = Field(
        ...,
        description="Created user information"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Account created successfully",
                "user": {
                    "username": "john_doe123",
                    "email": "john.doe@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "phone": "+1-555-123-4567",
                    "date_of_birth": "1990-05-15",
                    "marketing_emails_consent": False,
                    "created_at": "2025-07-09T10:30:00Z",
                    "updated_at": "2025-07-09T10:30:00Z"
                },
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