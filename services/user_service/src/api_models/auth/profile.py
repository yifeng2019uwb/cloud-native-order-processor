"""
Pydantic models specific to user profile API
Path: cloud-native-order-processor/services/user-service/src/models/profile_models.py
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime

from ..shared.common import SuccessResponse, ErrorResponse


class UserProfileResponse(BaseModel):
    """Response model for GET /auth/me - Complete user profile (without timestamps for security)"""

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

    class Config:
        json_encoders = {
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
                "marketing_emails_consent": False
            }
        }


class UserProfileUpdateRequest(BaseModel):
    """Request model for PUT /auth/me - Updateable fields only (JWT-only approach)"""

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

    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Smith",
                "email": "john.smith@example.com",
                "phone": "+1-555-987-6543",
                "date_of_birth": "1985-10-20",
                "marketing_emails_consent": True
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
                    "marketing_emails_consent": True,
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