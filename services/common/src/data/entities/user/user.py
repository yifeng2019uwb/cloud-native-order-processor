"""User entity models"""

from __future__ import annotations

import os
from datetime import date, datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field
from pynamodb.attributes import (BooleanAttribute, UnicodeAttribute,
                                 UTCDateTimeAttribute)
from pynamodb.indexes import AllProjection, GlobalSecondaryIndex
from pynamodb.models import Model

from ..entity_constants import (DatabaseFields, UserConstraints,
                                TimestampFields, UserConstants, UserFields)
from ...database.database_constants import AWSConfig, TableNames
from ..datetime_utils import get_current_utc
from .user_enums import DEFAULT_USER_ROLE


class User(BaseModel):
    """User domain model - pure business entity without database fields"""
    username: str = Field(..., max_length=UserConstraints.USERNAME_MAX_LENGTH, description="Username for easy access")
    email: str = Field(..., max_length=UserConstraints.EMAIL_MAX_LENGTH)
    password: str = Field(..., max_length=UserConstraints.PASSWORD_MAX_LENGTH, description="Hashed password")
    first_name: str = Field(..., max_length=UserConstraints.FIRST_NAME_MAX_LENGTH)
    last_name: str = Field(..., max_length=UserConstraints.LAST_NAME_MAX_LENGTH)
    phone: Optional[str] = Field(None, max_length=UserConstraints.PHONE_MAX_LENGTH)
    date_of_birth: Optional[date] = None
    marketing_emails_consent: bool = False
    role: str = Field(default=DEFAULT_USER_ROLE, max_length=UserConstraints.ROLE_MAX_LENGTH)
    created_at: datetime = Field(default_factory=get_current_utc)
    updated_at: datetime = Field(default_factory=get_current_utc)


# ==================== PYNAMODB MODEL ====================

class EmailIndex(GlobalSecondaryIndex):
    """Global Secondary Index for email lookups"""

    class Meta:
        """Meta class for EmailIndex"""
        index_name = UserConstants.EMAIL_INDEX_NAME
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    email = UnicodeAttribute(hash_key=True)
    username = UnicodeAttribute(range_key=True)


class UserItem(Model):
    """User PynamoDB model - handles DynamoDB operations"""

    # ==================== METADATA ====================

    class Meta:
        """Meta class for UserItem"""
        table_name = os.getenv(UserConstants.USERS_TABLE_ENV_VAR, TableNames.USERS)
        region = os.getenv(AWSConfig.AWS_REGION_ENV_VAR, AWSConfig.DEFAULT_REGION)
        billing_mode = AWSConfig.BILLING_MODE_PAY_PER_REQUEST

    # ==================== ATTRIBUTES ====================

    # Primary Key
    Pk = UnicodeAttribute(hash_key=True)
    Sk = UnicodeAttribute(range_key=True, default=UserFields.SK_VALUE)

    # User fields
    username = UnicodeAttribute()
    email = UnicodeAttribute()
    password_hash = UnicodeAttribute()
    first_name = UnicodeAttribute()
    last_name = UnicodeAttribute()
    phone = UnicodeAttribute(null=True)
    date_of_birth = UnicodeAttribute(null=True)
    marketing_emails_consent = BooleanAttribute(default=False)
    role = UnicodeAttribute(default=DEFAULT_USER_ROLE)

    # Timestamps
    created_at = UTCDateTimeAttribute(default=lambda: datetime.now(timezone.utc))
    updated_at = UTCDateTimeAttribute(default=lambda: datetime.now(timezone.utc))

    # Index
    email_index = EmailIndex()

    # ==================== CONVERSION ====================

    @classmethod
    def from_user(cls, user: User) -> UserItem:
        """Create UserItem from User domain model"""
        # Create PynamoDB model instance and set attributes explicitly
        user_item = cls()
        user_item.Pk = user.username
        user_item.Sk = UserFields.SK_VALUE
        user_item.username = user.username
        user_item.email = user.email
        user_item.password_hash = UserFields.HASHED_PASSWORD_MARKER  # Will be replaced with actual hash by DAO
        user_item.first_name = user.first_name
        user_item.last_name = user.last_name
        user_item.phone = user.phone
        user_item.date_of_birth = user.date_of_birth.isoformat() if user.date_of_birth else None
        user_item.marketing_emails_consent = user.marketing_emails_consent
        user_item.role = user.role
        user_item.created_at = user.created_at.replace(tzinfo=None)
        user_item.updated_at = user.updated_at.replace(tzinfo=None)
        return user_item

    def to_user(self) -> User:
        """Convert UserItem to User domain model"""
        # Convert PynamoDB attributes to dict, excluding database fields
        user_data = {
            UserFields.USERNAME: self.username,
            UserFields.EMAIL: self.email,
            UserFields.FIRST_NAME: self.first_name,
            UserFields.LAST_NAME: self.last_name,
            UserFields.PHONE: self.phone,
            UserFields.DATE_OF_BIRTH: self.date_of_birth,
            UserFields.MARKETING_EMAILS_CONSENT: self.marketing_emails_consent,
            UserFields.ROLE: self.role,
            TimestampFields.CREATED_AT: self.created_at.replace(tzinfo=timezone.utc),
            TimestampFields.UPDATED_AT: self.updated_at.replace(tzinfo=timezone.utc)
        }
        # Mark password as hashed - don't expose the actual hash
        user_data[UserFields.PASSWORD] = UserFields.HASHED_PASSWORD_MARKER
        return User(**user_data)

    # ==================== DATABASE OPERATIONS ====================

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
    # ==================== LIFECYCLE ====================

    def save(self, condition=None, **kwargs):
        """Override save to update timestamp"""
        # Convert timezone-aware datetime to naive UTC for PynamoDB UTCDateTimeAttribute
        self.updated_at = get_current_utc().replace(tzinfo=None)
        return super().save(condition=condition, **kwargs)
