from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
import re


class UserCreate(BaseModel):
    username: str  # ✅ Added username field
    email: EmailStr
    password: str
    name: str
    phone: Optional[str] = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        """Validate username format and constraints"""
        if not v or not v.strip():
            raise ValueError("Username cannot be empty")

        # Remove whitespace and convert to lowercase for consistency
        v = v.strip().lower()

        # Length validation
        if len(v) < 3 or len(v) > 30:
            raise ValueError("Username must be 3-30 characters long")

        # Format validation: only alphanumeric and underscores, cannot start/end with underscore
        if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9_]*[a-zA-Z0-9]$|^[a-zA-Z0-9]$', v):
            raise ValueError("Username can only contain letters, numbers, and underscores. Cannot start/end with underscore.")

        # No consecutive underscores
        if '__' in v:
            raise ValueError("Username cannot contain consecutive underscores")

        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 12 or len(v) > 20:
            raise ValueError("Password must be 12-20 characters long")

        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")

        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")

        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")

        if not re.search(r"[!@#$%^&*()\-_=+]", v):
            raise ValueError("Password must contain at least one special character (!@#$%^&*()-_=+)")

        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if v is None:
            return v
        # Basic phone validation - can be enhanced later
        phone_clean = re.sub(r'[^\d]', '', v)
        if len(phone_clean) < 10 or len(phone_clean) > 15:
            raise ValueError("Phone number must be 10-15 digits")
        return v


class UserLogin(BaseModel):
    # ✅ Support login with either username or email
    identifier: str  # Can be username or email
    password: str

    @field_validator("identifier")
    @classmethod
    def validate_identifier(cls, v):
        if not v or not v.strip():
            raise ValueError("Username or email cannot be empty")
        return v.strip()


class User(BaseModel):
    username: str  # ✅ Added username field
    email: str
    name: str
    phone: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class UserResponse(BaseModel):
    username: str  # ✅ Added username field
    email: str
    name: str
    phone: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"