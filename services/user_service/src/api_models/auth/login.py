"""
Pydantic models specific to user login API
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional

# Import centralized field validation functions
from validation.field_validators import (
    validate_username, validate_password
)

# Import custom exceptions
from common.exceptions import CNOPEntityValidationException

# Constants for field names
USERNAME_FIELD = "username"
PASSWORD_FIELD = "password"


class UserLoginRequest(BaseModel):
    """Request model for POST /auth/login"""
    username: str = Field(..., min_length=6, max_length=30, description="Username")
    password: str = Field(..., min_length=12, max_length=20, description="Password")

    @field_validator(USERNAME_FIELD)
    @classmethod
    def validate_username_format(cls, v: str) -> str:
        """Basic format validation for username"""
        return validate_username(v)

    @field_validator(PASSWORD_FIELD)
    @classmethod
    def validate_password_format(cls, v: str) -> str:
        """Basic format validation for password"""
        return validate_password(v)


class LoginResponse(BaseModel):
    """Response model for successful user login"""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")