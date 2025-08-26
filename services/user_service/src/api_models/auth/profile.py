"""
Pydantic models specific to user profile API
Path: cloud-native-order-processor/services/user-service/src/models/profile_models.py

Layer 1: Model validation (field format, basic sanitization)
Layer 2: Business validation (in service layer)
"""
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional
from datetime import date

from ..shared.common import UserBaseInfo, SuccessResponse, ErrorResponse

# Import centralized field validation functions
from validation.field_validators import (
    validate_name, validate_email, validate_phone, validate_date_of_birth
)

# Import custom exceptions
from common.exceptions import CNOPEntityValidationException


class UserProfileResponse(UserBaseInfo):
    """Response model for user profile data"""

    phone: Optional[str] = Field(
        None,
        description="Phone number (optional)"
    )

    date_of_birth: Optional[date] = Field(
        None,
        description="Date of birth (optional)"
    )

    model_config = ConfigDict(
        json_schema_extra={
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
    )


class UserProfileUpdateRequest(BaseModel):
    """
    Request model for PUT /users/profile

    Layer 1 Validation: Field format, basic sanitization
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "phone": "+1-555-123-4567",
                "date_of_birth": "1990-05-15"
            }
        }
    )

    first_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        strip_whitespace=True,
        description="User first name (1-50 characters)",
        example="John"
    )

    last_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        strip_whitespace=True,
        description="User last name (1-50 characters)",
        example="Doe"
    )

    email: Optional[EmailStr] = Field(
        None,
        description="User email address (must be valid email format)",
        example="john.doe@example.com"
    )

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

    @field_validator('first_name')
    @classmethod
    def validate_first_name_format(cls, v: Optional[str]) -> Optional[str]:
        """Layer 1: Basic format validation for first name"""
        if v is None:
            return v
        return validate_name(v)

    @field_validator('last_name')
    @classmethod
    def validate_last_name_format(cls, v: Optional[str]) -> Optional[str]:
        """Layer 1: Basic format validation for last name"""
        if v is None:
            return v
        return validate_name(v)

    @field_validator('email')
    @classmethod
    def validate_email_format(cls, v: Optional[str]) -> Optional[str]:
        """Layer 1: Basic format validation for email"""
        if v is None:
            return v
        return validate_email(v)

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


class ProfileUpdateSuccessResponse(SuccessResponse):
    """Success response wrapper for profile update"""

    message: str = Field(
        default="Profile updated successfully",
        description="Profile update success message"
    )

    user: UserProfileResponse = Field(
        ...,
        description="Updated user profile data"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Profile updated successfully",
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
    )


class ProfileUpdateErrorResponse(ErrorResponse):
    """Error response specific to profile update failures"""

    error: str = Field(
        default="PROFILE_UPDATE_FAILED",
        description="Profile update error code"
    )

    message: str = Field(
        default="Failed to update profile. Please try again.",
        description="Profile update error message"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": False,
                "error": "PROFILE_UPDATE_FAILED",
                "message": "Failed to update profile. Please try again.",
                "details": None,
                "timestamp": "2025-07-09T10:30:00Z"
            }
        }
    )