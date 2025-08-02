from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime
from .user_enums import UserRole, DEFAULT_USER_ROLE, VALID_ROLES


class UserCreate(BaseModel):
    """User creation model with simple DB constraints only"""
    username: str = Field(..., max_length=30)
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., max_length=128)  # Hashed password length
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    phone: Optional[str] = Field(None, max_length=15)
    date_of_birth: Optional[date] = None
    marketing_emails_consent: bool = False
    role: str = Field(default=DEFAULT_USER_ROLE, max_length=20)


class UserLogin(BaseModel):
    """User login model with simple DB constraints only"""
    username: str = Field(..., max_length=30)
    password: str = Field(..., max_length=128)  # Hashed password length


class User(BaseModel):
    """User entity model with simple DB constraints only"""
    Pk: str = Field(..., description="Primary key (username)")
    username: str = Field(..., max_length=30, description="Username for easy access")
    email: str = Field(..., max_length=255)
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    phone: Optional[str] = Field(None, max_length=15)
    date_of_birth: Optional[date] = None
    marketing_emails_consent: bool = False
    role: str = Field(default=DEFAULT_USER_ROLE, max_length=20)
    created_at: datetime
    updated_at: datetime


class UserResponse(BaseModel):
    """User response model with simple DB constraints only"""
    username: str = Field(..., max_length=30)
    email: str = Field(..., max_length=255)
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    phone: Optional[str] = Field(None, max_length=15)
    role: str = Field(default=DEFAULT_USER_ROLE, max_length=20)
    created_at: datetime
    updated_at: datetime
