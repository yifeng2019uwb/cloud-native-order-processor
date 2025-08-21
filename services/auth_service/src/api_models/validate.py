"""
API models for JWT token validation endpoint.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ValidateTokenRequest(BaseModel):
    """Request model for JWT token validation."""

    token: str = Field(..., description="JWT token to validate")
    request_id: Optional[str] = Field(None, description="Optional request ID for correlation")


class ValidateTokenResponse(BaseModel):
    """Response model for successful JWT token validation."""

    valid: bool = Field(True, description="Token validation result")
    user: str = Field(..., description="Username from token")
    expires_at: str = Field(..., description="Token expiration timestamp")
    created_at: Optional[str] = Field(None, description="Token creation timestamp")
    metadata: Dict[str, Any] = Field(..., description="Token metadata")
    request_id: Optional[str] = Field(None, description="Request ID for correlation")


class ValidateTokenErrorResponse(BaseModel):
    """Response model for failed JWT token validation."""

    valid: bool = Field(False, description="Token validation result")
    error: str = Field(..., description="Error type identifier")
    message: str = Field(..., description="Human-readable error message")
    request_id: Optional[str] = Field(None, description="Request ID for correlation")
