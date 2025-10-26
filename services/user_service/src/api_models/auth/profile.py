"""
Pydantic models specific to user profile API
"""
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional
from datetime import date

from ..shared.common import UserBaseInfo

# Import centralized field validation functions
from validation.field_validators import (
    validate_name, validate_email, validate_phone, validate_date_of_birth
)

# Import custom exceptions
from common.exceptions import CNOPEntityValidationException

# Constants for field names
USERNAME_FIELD = "username"
EMAIL_FIELD = "email"
FIRST_NAME_FIELD = "first_name"
LAST_NAME_FIELD = "last_name"
PHONE_FIELD = "phone"
DATE_OF_BIRTH_FIELD = "date_of_birth"


class UserProfileResponse(UserBaseInfo):
    """Response model for user profile data"""
    phone: Optional[str] = Field(None, description="Phone number")
    date_of_birth: Optional[date] = Field(None, description="Date of birth")


class UserProfileUpdateRequest(BaseModel):
    """Request model for PUT /users/profile"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50, description="First name")
    last_name: Optional[str] = Field(None, min_length=1, max_length=50, description="Last name")
    email: Optional[EmailStr] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    date_of_birth: Optional[date] = Field(None, description="Date of birth")

    @field_validator(FIRST_NAME_FIELD)
    @classmethod
    def validate_first_name_format(cls, v: Optional[str]) -> Optional[str]:
        """Layer 1: Basic format validation for first name"""
        if v is None:
            return v
        return validate_name(v)

    @field_validator(LAST_NAME_FIELD)
    @classmethod
    def validate_last_name_format(cls, v: Optional[str]) -> Optional[str]:
        """Layer 1: Basic format validation for last name"""
        if v is None:
            return v
        return validate_name(v)

    @field_validator(EMAIL_FIELD)
    @classmethod
    def validate_email_format(cls, v: Optional[str]) -> Optional[str]:
        """Layer 1: Basic format validation for email"""
        if v is None:
            return v
        return validate_email(v)

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


class ProfileResponse(BaseModel):
    """Response model for successful profile update"""
    message: str = "Profile updated successfully"
    user: UserProfileResponse