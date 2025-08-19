"""
Pydantic models specific to user login API
Path: cloud-native-order-processor/services/user-service/src/models/login_models.py

Layer 1: Model validation (field format, basic sanitization)
Layer 2: Business validation (in service layer)
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional

from ..shared.common import SuccessResponse, ErrorResponse

# Import centralized field validation functions
from validation.field_validators import (
    validate_username, validate_password
)

# Import custom exceptions
from common.exceptions.shared_exceptions import UserValidationException


class UserLoginRequest(BaseModel):
    """
    Request model for POST /auth/login

    Layer 1 Validation: Field format, basic sanitization
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "john_doe123",
                "password": "SecurePassword123!"
            }
        }
    )

    username: str = Field(
        ...,
        min_length=6,
        max_length=30,
        strip_whitespace=True,
        description="User username (6-30 characters)",
        example="john_doe123"
    )

    password: str = Field(
        ...,
        min_length=12,
        max_length=20,
        description="User password (12-20 characters with complexity requirements)",
        example="SecurePassword123!"
    )

    @field_validator('username')
    @classmethod
    def validate_username_format(cls, v: str) -> str:
        """Layer 1: Basic format validation for username"""
        return validate_username(v)

    @field_validator('password')
    @classmethod
    def validate_password_format(cls, v: str) -> str:
        """Layer 1: Basic format validation for password"""
        return validate_password(v)


class UserLoginResponse(BaseModel):
    """Response model for successful user login"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600
            }
        }
    )

    access_token: str = Field(
        ...,
        description="JWT access token for authentication",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    )

    token_type: str = Field(
        default="bearer",
        description="Token type (always 'bearer')",
        example="bearer"
    )

    expires_in: int = Field(
        ...,
        description="Token expiration time in seconds",
        example=3600
    )


class LoginSuccessResponse(SuccessResponse):
    """Success response wrapper for login"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Login successful",
                "data": {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "expires_in": 3600
                },
                "timestamp": "2025-07-09T10:30:00Z"
            }
        }
    )

    data: UserLoginResponse = Field(
        ...,
        description="Login response data"
    )


class LoginErrorResponse(ErrorResponse):
    """Error response specific to login failures"""

    error: str = Field(
        default="LOGIN_FAILED",
        description="Login error code"
    )

    message: str = Field(
        default="Login failed. Please check your credentials and try again.",
        description="Login error message"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": False,
                "error": "LOGIN_FAILED",
                "message": "Login failed. Please check your credentials and try again.",
                "details": None,
                "timestamp": "2025-07-09T10:30:00Z"
            }
        }
    )