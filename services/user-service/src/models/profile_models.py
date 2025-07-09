"""
Pydantic models specific to user profile API
Path: cloud-native-order-processor/services/user-service/src/models/profile_models.py
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import date, datetime
import re

from .shared_models import SuccessResponse, ErrorResponse


class UserProfileResponse(BaseModel):
    """Response model for GET /auth/me - Complete user profile"""

    username: str = Field(
        ...,
        description="Unique username"
    )

    email: str = Field(
        ...,
        description="User email address"
    )

    first_name: str = Field(
        ...,
        description="User first name"
    )

    last_name: str = Field(
        ...,
        description="User last name"
    )

    phone: Optional[str] = Field(
        None,
        description="User phone number"
    )

    date_of_birth: Optional[date] = Field(
        None,
        description="User date of birth"
    )

    marketing_emails_consent: bool = Field(
        ...,
        description="Marketing emails consent status"
    )

    created_at: datetime = Field(
        ...,
        description="Account creation timestamp"
    )

    updated_at: datetime = Field(
        ...,
        description="Last update timestamp"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "username": "john_doe123",
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+1-555-123-4567",
                "date_of_birth": "1990-05-15",
                "marketing_emails_consent": false,
                "created_at": "2025-07-09T10:30:00Z",
                "updated_at": "2025-07-09T10:30:00Z"
            }
        }


class UserProfileUpdateRequest(BaseModel):
    """Request model for PUT /auth/me - Updateable fields only"""

    # Note: username is NOT updateable (should remain stable identifier)

    first_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        strip_whitespace=True,
        description="Updated first name (optional)"
    )

    last_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        strip_whitespace=True,
        description="Updated last name (optional)"
    )

    email: Optional[EmailStr] = Field(
        None,
        description="Updated email address (optional)"
    )

    phone: Optional[str] = Field(
        None,
        min_length=10,
        max_length=20,
        description="Updated phone number (optional)"
    )

    date_of_birth: Optional[date] = Field(
        None,
        description="Updated date of birth (optional)"
    )

    marketing_emails_consent: Optional[bool] = Field(
        None,
        description="Updated marketing emails consent (optional)"
    )

    @validator('first_name')
    def validate_first_name_format(cls, v):
        """Validate first name contains only letters if provided"""
        if v is not None and not re.match(r"^[a-zA-Z]+$", v):
            raise ValueError('First name can only contain letters')
        return v.title() if v else v

    @validator('last_name')
    def validate_last_name_format(cls, v):
        """Validate last name contains only letters if provided"""
        if v is not None and not re.match(r"^[a-zA-Z]+$", v):
            raise ValueError('Last name can only contain letters')
        return v.title() if v else v

    @validator('phone')
    def validate_phone_format(cls, v):
        """Validate phone number format if provided"""
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
        """Validate date of birth if provided"""
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
            raise ValueError('Must be at least 13 years old')

        # Check maximum reasonable age (120 years)
        max_age_date = today - timedelta(days=120 * 365.25)
        if v < max_age_date:
            raise ValueError('Invalid date of birth')

        return v

    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Smith",
                "email": "john.smith@example.com",
                "phone": "+1-555-987-6543",
                "date_of_birth": "1990-05-15",
                "marketing_emails_consent": true
            }
        }


class ProfileUpdateSuccessResponse(SuccessResponse):
    """Success response for profile update"""

    message: str = Field(
        default="Profile updated successfully",
        description="Profile update success message"
    )

    user: UserProfileResponse = Field(
        ...,
        description="Updated user profile information"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Profile updated successfully",
                "user": {
                    "username": "john_doe123",
                    "email": "john.smith@example.com",
                    "first_name": "John",
                    "last_name": "Smith",
                    "phone": "+1-555-987-6543",
                    "date_of_birth": "1990-05-15",
                    "marketing_emails_consent": true,
                    "created_at": "2025-07-09T10:30:00Z",
                    "updated_at": "2025-07-09T12:45:00Z"
                },
                "timestamp": "2025-07-09T12:45:00Z"
            }
        }


class ProfileUpdateErrorResponse(ErrorResponse):
    """Error response for profile update failures"""

    error: str = Field(
        default="PROFILE_UPDATE_FAILED",
        description="Profile update error code"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "PROFILE_UPDATE_FAILED",
                "message": "Failed to update profile. Please try again.",
                "details": None,
                "timestamp": "2025-07-09T10:30:00Z"
            }
        }