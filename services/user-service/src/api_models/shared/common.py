"""
Shared Pydantic models used across all authentication APIs
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime, date


class BaseResponse(BaseModel):
    """Base response model with common fields"""

    success: bool = Field(
        default=True,
        description="Operation success indicator"
    )

    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response timestamp"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SuccessResponse(BaseResponse):
    """Standard success response model"""

    message: str = Field(
        ...,
        max_length=200,
        description="Success message"
    )

    data: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional response data"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {},
                "timestamp": "2025-07-09T10:30:00Z"
            }
        }


    """Validation error response with field-specific details"""

    error: str = Field(
        default="VALIDATION_ERROR",
        description="Validation error code"
    )

    validation_errors: Optional[list] = Field(
        None,
        description="List of validation errors (generic, safe for client)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "VALIDATION_ERROR",
                "message": "The provided data is invalid",
                "validation_errors": [
                    {
                        "field": "email",
                        "message": "Please enter a valid email address"
                    }
                ],
                "timestamp": "2025-07-09T10:30:00Z"
            }
        }


class TokenResponse(BaseModel):
    """JWT token response model"""

    access_token: str = Field(
        ...,
        description="JWT access token"
    )

    token_type: str = Field(
        default="bearer",
        description="Token type (always 'bearer')"
    )

    expires_in: Optional[int] = Field(
        None,
        description="Token expiration time in seconds"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 86400
            }
        }


class UserBaseInfo(BaseModel):

    """Base user information model (safe for client responses)"""

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
                "marketing_emails_consent": False,
                "created_at": "2025-07-09T10:30:00Z",
                "updated_at": "2025-07-09T10:30:00Z"
            }
        }

class ErrorResponse(BaseResponse):
    """Standard error response model for client-facing errors"""

    success: bool = Field(
        default=False,
        description="Operation success indicator"
    )

    error: str = Field(
        ...,
        max_length=50,
        description="Error code"
    )

    message: str = Field(
        ...,
        max_length=200,
        description="Human-readable error message"
    )

    details: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional error context (safe for client)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "INVALID_INPUT",
                "message": "The provided information is invalid",
                "details": None,
                "timestamp": "2025-07-09T10:30:00Z"
            }
        }


class ValidationErrorResponse(ErrorResponse):
    """Validation error response with field-specific details"""

    error: str = Field(
        default="VALIDATION_ERROR",
        description="Validation error code"
    )

    validation_errors: Optional[list] = Field(
        None,
        description="List of validation errors (generic, safe for client)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "VALIDATION_ERROR",
                "message": "The provided data is invalid",
                "validation_errors": [
                    {
                        "field": "email",
                        "message": "Please enter a valid email address"
                    }
                ],
                "timestamp": "2025-07-09T10:30:00Z"
            }
        }