from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
import re


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: str
    last_name: str
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
        if len(v) < 6 or len(v) > 30:
            raise ValueError("Username must be 6-30 characters long")

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

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, v):
        if not v or not v.strip():
            raise ValueError("First name cannot be empty")
        return v.strip()

    @field_validator("last_name")
    @classmethod
    def validate_last_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Last name cannot be empty")
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
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if not v or not v.strip():
            raise ValueError("Username or email cannot be empty")
        return v.strip()


class User(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @property
    def name(self) -> str:
        """Computed full name for backward compatibility"""
        return f"{self.first_name} {self.last_name}".strip()


class UserResponse(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @property
    def name(self) -> str:
        """Computed full name for backward compatibility"""
        return f"{self.first_name} {self.last_name}".strip()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"