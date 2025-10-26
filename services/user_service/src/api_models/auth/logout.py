"""
Pydantic models specific to user logout API
"""
from pydantic import BaseModel


class LogoutRequest(BaseModel):
    """Request model for POST /auth/logout - Empty for JWT stateless approach"""
    pass


class LogoutResponse(BaseModel):
    """Response model for successful user logout"""
    message: str = "Logged out successfully"