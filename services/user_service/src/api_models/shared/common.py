"""
Shared Pydantic models used across all authentication APIs
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date


class UserBaseInfo(BaseModel):

    """Base user information model (safe for client responses) - TODO: Implement data masking for sensitive fields"""

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