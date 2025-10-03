"""User entity models"""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from ..entity_constants import DatabaseFields, FieldConstraints, UserFields
from .user_enums import DEFAULT_USER_ROLE


class User(BaseModel):
    """User domain model - pure business entity without database fields"""
    username: str = Field(..., max_length=FieldConstraints.USERNAME_MAX_LENGTH, description="Username for easy access")
    email: str = Field(..., max_length=FieldConstraints.EMAIL_MAX_LENGTH)
    password: str = Field(..., max_length=FieldConstraints.PASSWORD_MAX_LENGTH, description="Hashed password")
    first_name: str = Field(..., max_length=FieldConstraints.FIRST_NAME_MAX_LENGTH)
    last_name: str = Field(..., max_length=FieldConstraints.LAST_NAME_MAX_LENGTH)
    phone: Optional[str] = Field(None, max_length=FieldConstraints.PHONE_MAX_LENGTH)
    date_of_birth: Optional[date] = None
    marketing_emails_consent: bool = False
    role: str = Field(default=DEFAULT_USER_ROLE, max_length=FieldConstraints.ROLE_MAX_LENGTH)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserItem(BaseModel):
    """User database model - includes DynamoDB fields (Pk, Sk)"""
    Pk: str = Field(..., description="Primary key (username)")
    Sk: str = Field(default=UserFields.SK_VALUE, description="Sort key (USER)")
    username: str = Field(..., max_length=FieldConstraints.USERNAME_MAX_LENGTH, description="Username for easy access")
    email: str = Field(..., max_length=FieldConstraints.EMAIL_MAX_LENGTH)
    password_hash: str = Field(..., max_length=FieldConstraints.PASSWORD_MAX_LENGTH, description="Hashed password")
    first_name: str = Field(..., max_length=FieldConstraints.FIRST_NAME_MAX_LENGTH)
    last_name: str = Field(..., max_length=FieldConstraints.LAST_NAME_MAX_LENGTH)
    phone: Optional[str] = Field(None, max_length=FieldConstraints.PHONE_MAX_LENGTH)
    date_of_birth: Optional[date] = None
    marketing_emails_consent: bool = False
    role: str = Field(default=DEFAULT_USER_ROLE, max_length=FieldConstraints.ROLE_MAX_LENGTH)
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    def get_key(self) -> dict:
        """Get database key for this user item"""
        return {
            DatabaseFields.PK: self.Pk,
            DatabaseFields.SK: self.Sk
        }

    @staticmethod
    def get_key_for_username(username: str) -> dict:
        """Get database key for a username (static method)"""
        return {
            DatabaseFields.PK: username,
            DatabaseFields.SK: UserFields.SK_VALUE
        }

    @classmethod
    def from_user(cls, user: User) -> UserItem:
        """Create UserItem from User domain model"""
        user_data = user.model_dump()
        # Map password to password_hash for database storage
        user_data[UserFields.PASSWORD_HASH] = user_data.pop(UserFields.PASSWORD)
        return cls(
            Pk=user.username,
            Sk=UserFields.SK_VALUE,
            **user_data
        )

    def to_user(self) -> User:
        """Convert UserItem to User domain model"""
        user_data = self.model_dump(exclude={DatabaseFields.PK, DatabaseFields.SK, UserFields.PASSWORD_HASH})
        # Mark password as hashed - don't expose the actual hash
        user_data[UserFields.PASSWORD] = UserFields.HASHED_PASSWORD_MARKER
        return User(**user_data)
