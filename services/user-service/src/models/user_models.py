"""
Internal user models for DAO layer and database operations
Path: cloud-native-order-processor/services/user-service/src/models/user_models.py
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, date


class User(BaseModel):
    """
    Internal user entity with all fields including sensitive data
    Used for business logic and internal operations
    """

    # Primary identifiers
    user_id: str = Field(
        ...,
        description="Unique user identifier (UUID or similar)"
    )

    username: str = Field(
        ...,
        description="Unique username"
    )

    email: str = Field(
        ...,
        description="Unique email address"
    )

    # Sensitive data (never exposed to client)
    password_hash: str = Field(
        ...,
        description="Hashed password (bcrypt or similar)"
    )

    # Personal information
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
        default=False,
        description="Marketing emails consent status"
    )

    # System metadata
    created_at: datetime = Field(
        ...,
        description="Account creation timestamp"
    )

    updated_at: datetime = Field(
        ...,
        description="Last update timestamp"
    )

    # Additional internal fields
    is_active: bool = Field(
        default=True,
        description="Account active status"
    )

    last_login: Optional[datetime] = Field(
        None,
        description="Last login timestamp"
    )

    email_verified: bool = Field(
        default=False,
        description="Email verification status"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }


class UserCreate(BaseModel):
    """
    Model for creating new user in database (DAO layer)
    Contains registration data + processed fields
    """

    username: str = Field(
        ...,
        description="Unique username (lowercase)"
    )

    email: str = Field(
        ...,
        description="Unique email address"
    )

    password_hash: str = Field(
        ...,
        description="Hashed password"
    )

    first_name: str = Field(
        ...,
        description="User first name (title case)"
    )

    last_name: str = Field(
        ...,
        description="User last name (title case)"
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
        default=False,
        description="Marketing emails consent"
    )

    # Auto-generated fields
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Account creation timestamp"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )

    is_active: bool = Field(
        default=True,
        description="Account active status"
    )

    email_verified: bool = Field(
        default=False,
        description="Email verification status"
    )


class UserUpdate(BaseModel):
    """
    Model for updating user in database (DAO layer)
    Only contains updateable fields
    """

    first_name: Optional[str] = Field(
        None,
        description="Updated first name"
    )

    last_name: Optional[str] = Field(
        None,
        description="Updated last name"
    )

    email: Optional[str] = Field(
        None,
        description="Updated email address"
    )

    phone: Optional[str] = Field(
        None,
        description="Updated phone number"
    )

    date_of_birth: Optional[date] = Field(
        None,
        description="Updated date of birth"
    )

    marketing_emails_consent: Optional[bool] = Field(
        None,
        description="Updated marketing consent"
    )

    # System fields that can be updated
    last_login: Optional[datetime] = Field(
        None,
        description="Last login timestamp"
    )

    email_verified: Optional[bool] = Field(
        None,
        description="Email verification status"
    )

    is_active: Optional[bool] = Field(
        None,
        description="Account active status"
    )

    # Auto-updated
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Update timestamp"
    )


class UserInDB(BaseModel):
    """
    DynamoDB-specific user representation
    Maps to actual database structure and indexes
    """

    # DynamoDB primary key structure
    PK: str = Field(
        ...,
        description="Partition key: USER#{user_id}"
    )

    SK: str = Field(
        default="PROFILE",
        description="Sort key: PROFILE for main user data"
    )

    # GSI for email lookup
    email: str = Field(
        ...,
        description="Email for EmailIndex GSI"
    )

    # GSI for username lookup
    username: str = Field(
        ...,
        description="Username for UsernameIndex GSI"
    )

    # All user data as attributes
    user_id: str = Field(
        ...,
        description="User ID extracted from PK"
    )

    password_hash: str = Field(
        ...,
        description="Hashed password"
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

    date_of_birth: Optional[str] = Field(
        None,
        description="Date of birth as ISO string"
    )

    marketing_emails_consent: bool = Field(
        default=False,
        description="Marketing emails consent"
    )

    created_at: str = Field(
        ...,
        description="Creation timestamp as ISO string"
    )

    updated_at: str = Field(
        ...,
        description="Update timestamp as ISO string"
    )

    is_active: bool = Field(
        default=True,
        description="Account active status"
    )

    last_login: Optional[str] = Field(
        None,
        description="Last login as ISO string"
    )

    email_verified: bool = Field(
        default=False,
        description="Email verification status"
    )

    # DynamoDB metadata
    entity_type: str = Field(
        default="USER",
        description="Entity type for querying"
    )