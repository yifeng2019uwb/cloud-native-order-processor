"""
Pydantic models specific to user login API
Path: cloud-native-order-processor/services/user-service/src/models/login_models.py
"""
from pydantic import BaseModel, Field
from ..shared.common import SuccessResponse, ErrorResponse, TokenResponse, UserBaseInfo


class UserLoginRequest(BaseModel):
    """Request model for POST /auth/login"""

    username: str = Field(
        ...,
        min_length=6,
        max_length=30,
        strip_whitespace=True,
        description="Username for login",
        example="john_doe123"
    )

    password: str = Field(
        ...,
        min_length=12,
        max_length=20,
        description="User password",
        example="SecurePassword123!"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe123",
                "password": "SecurePassword123!"
            }
        }


class LoginSuccessResponse(SuccessResponse):
    """Success response for login with token and user info"""

    message: str = Field(
        default="Login successful",
        description="Login success message"
    )

    access_token: str = Field(
        ...,
        description="JWT access token"
    )

    token_type: str = Field(
        default="bearer",
        description="Token type"
    )

    expires_in: int = Field(
        default=86400,
        description="Token expiration time in seconds"
    )

    user: UserBaseInfo = Field(
        ...,
        description="Basic user information"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Login successful",
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 86400,
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


class LoginErrorResponse(ErrorResponse):
    """Error response specific to login failures"""

    error: str = Field(
        default="AUTHENTICATION_FAILED",
        description="Login error code"
    )

    message: str = Field(
        default="Invalid credentials. Please check your username and password.",
        description="Generic login error message for security"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "AUTHENTICATION_FAILED",
                "message": "Invalid credentials. Please check your username and password.",
                "details": None,
                "timestamp": "2025-07-09T10:30:00Z"
            }
        }