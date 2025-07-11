from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime
import re


class AssetCreate(BaseModel):
    """Request model for creating new crypto assets"""

    asset_id: str = Field(
        ...,
        min_length=3,
        max_length=6,
        description="Asset symbol (3-6 characters, uppercase)",
        example="BTC"
    )

    name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        strip_whitespace=True,
        description="Asset full name",
        example="Bitcoin"
    )

    description: Optional[str] = Field(
        None,
        min_length=0,
        max_length=1000,
        strip_whitespace=True,
        description="Asset description (optional)",
        example="Digital currency and store of value"
    )

    category: str = Field(
        ...,
        description="Asset category",
        example="major"
    )

    amount: float = Field(
        ...,
        ge=0,
        description="Available inventory amount",
        example=500.25
    )

    price_usd: float = Field(
        ...,
        ge=0,
        description="Current USD price",
        example=45000.50
    )

    @field_validator("asset_id")
    @classmethod
    def validate_asset_id(cls, v):
        """Validate asset symbol format"""
        if not v or not v.strip():
            raise ValueError("Asset ID cannot be empty")

        # Convert to uppercase and strip whitespace
        v = v.strip().upper()

        # Must be 3-6 characters, alphanumeric only
        if not re.match(r'^[A-Z0-9]{3,6}$', v):
            raise ValueError("Asset ID must be 3-6 uppercase letters/numbers only")

        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        """Validate asset name"""
        if not v or not v.strip():
            raise ValueError("Asset name cannot be empty")

        # Strip whitespace and convert to title case
        v = v.strip().title()

        # Basic format validation - letters, numbers, spaces allowed
        if not re.match(r'^[a-zA-Z0-9\s\-\.]+$', v):
            raise ValueError("Asset name contains invalid characters")

        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls, v):
        """Validate asset category"""
        valid_categories = ["major", "altcoin", "stablecoin"]

        if v.lower() not in valid_categories:
            raise ValueError(f"Category must be one of: {', '.join(valid_categories)}")

        return v.lower()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v):
        """Validate description if provided"""
        if v is None:
            return v

        # Strip whitespace
        v = v.strip()

        # Allow empty description
        if len(v) == 0:
            return v

        # Check length
        if len(v) > 1000:
            raise ValueError("Description cannot exceed 1000 characters")

        return v

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        """Validate inventory amount"""
        if v < 0:
            raise ValueError("Amount cannot be negative")

        # Round to 8 decimal places (crypto precision)
        return round(v, 8)

    @field_validator("price_usd")
    @classmethod
    def validate_price_usd(cls, v):
        """Validate USD price"""
        if v < 0:
            raise ValueError("Price cannot be negative")

        # Round to 2 decimal places (USD precision)
        return round(v, 2)

    class Config:
        json_schema_extra = {
            "example": {
                "asset_id": "BTC",
                "name": "Bitcoin",
                "description": "Digital currency and store of value",
                "category": "major",
                "amount": 500.25,
                "price_usd": 45000.50
            }
        }


class Asset(BaseModel):
    """Core asset entity model"""

    asset_id: str = Field(
        ...,
        description="Asset symbol (primary key)"
    )

    name: str = Field(
        ...,
        description="Asset full name"
    )

    description: Optional[str] = Field(
        None,
        description="Asset description"
    )

    category: str = Field(
        ...,
        description="Asset category (major/altcoin/stablecoin)"
    )

    amount: float = Field(
        ...,
        description="Available inventory amount"
    )

    price_usd: float = Field(
        ...,
        description="Current USD price"
    )

    is_active: bool = Field(
        default=True,
        description="Whether asset is available for trading"
    )

    created_at: datetime = Field(
        ...,
        description="Asset creation timestamp"
    )

    updated_at: datetime = Field(
        ...,
        description="Last update timestamp"
    )

    @model_validator(mode='after')
    def validate_price_active_relationship(self):
        """Validate price and active status relationship"""
        if self.price_usd == 0 and self.is_active:
            raise ValueError("Asset cannot be active with zero price")

        return self

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "asset_id": "BTC",
                "name": "Bitcoin",
                "description": "Digital currency and store of value",
                "category": "major",
                "amount": 500.25,
                "price_usd": 45000.50,
                "is_active": True,
                "created_at": "2025-07-11T09:00:00Z",
                "updated_at": "2025-07-11T10:30:00Z"
            }
        }


class AssetResponse(BaseModel):
    """Safe asset model for API responses"""

    asset_id: str = Field(
        ...,
        description="Asset symbol"
    )

    name: str = Field(
        ...,
        description="Asset full name"
    )

    description: Optional[str] = Field(
        None,
        description="Asset description"
    )

    category: str = Field(
        ...,
        description="Asset category"
    )

    amount: float = Field(
        ...,
        description="Available inventory amount"
    )

    price_usd: float = Field(
        ...,
        description="Current USD price"
    )

    is_active: bool = Field(
        ...,
        description="Whether asset is available for trading"
    )

    created_at: datetime = Field(
        ...,
        description="Asset creation timestamp"
    )

    updated_at: datetime = Field(
        ...,
        description="Last update timestamp"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "asset_id": "BTC",
                "name": "Bitcoin",
                "description": "Digital currency and store of value",
                "category": "major",
                "amount": 500.25,
                "price_usd": 45000.50,
                "is_active": True,
                "created_at": "2025-07-11T09:00:00Z",
                "updated_at": "2025-07-11T10:30:00Z"
            }
        }


class AssetUpdate(BaseModel):
    """Model for updating existing assets (asset_id and name cannot be changed)"""

    description: Optional[str] = Field(
        None,
        min_length=0,
        max_length=1000,
        strip_whitespace=True,
        description="Updated asset description"
    )

    category: Optional[str] = Field(
        None,
        description="Updated asset category"
    )

    amount: Optional[float] = Field(
        None,
        ge=0,
        description="Updated inventory amount"
    )

    price_usd: Optional[float] = Field(
        None,
        ge=0,
        description="Updated USD price"
    )

    is_active: Optional[bool] = Field(
        None,
        description="Updated active status"
    )

    @field_validator("category")
    @classmethod
    def validate_category(cls, v):
        """Validate category if provided"""
        if v is None:
            return v

        valid_categories = ["major", "altcoin", "stablecoin"]

        if v.lower() not in valid_categories:
            raise ValueError(f"Category must be one of: {', '.join(valid_categories)}")

        return v.lower()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v):
        """Validate description if provided"""
        if v is None:
            return v

        # Strip whitespace
        v = v.strip()

        # Allow empty description
        if len(v) == 0:
            return v

        return v

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        """Validate amount if provided"""
        if v is None:
            return v

        if v < 0:
            raise ValueError("Amount cannot be negative")

        # Round to 8 decimal places (crypto precision)
        return round(v, 8)

    @field_validator("price_usd")
    @classmethod
    def validate_price_usd(cls, v):
        """Validate price if provided"""
        if v is None:
            return v

        if v < 0:
            raise ValueError("Price cannot be negative")

        # Round to 2 decimal places (USD precision)
        return round(v, 2)

    @model_validator(mode='after')
    def validate_price_active_relationship(self):
        """Validate price and active relationship if both are being updated"""
        # Only validate if both fields are provided in the update
        if self.price_usd is not None and self.is_active is not None:
            if self.price_usd == 0 and self.is_active:
                raise ValueError("Asset cannot be active with zero price")

        return self

    class Config:
        json_schema_extra = {
            "example": {
                "description": "Updated description",
                "category": "major",
                "amount": 750.50,
                "price_usd": 47000.25,
                "is_active": True
            }
        }


# Asset list response for API endpoints
class AssetListResponse(BaseModel):
    """Response model for asset list endpoints"""

    assets: list[AssetResponse] = Field(
        ...,
        description="List of assets"
    )

    total_count: int = Field(
        ...,
        description="Total number of assets"
    )

    active_count: int = Field(
        ...,
        description="Number of active assets"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "assets": [
                    {
                        "asset_id": "BTC",
                        "name": "Bitcoin",
                        "description": "Digital currency",
                        "category": "major",
                        "amount": 500.25,
                        "price_usd": 45000.50,
                        "is_active": True,
                        "created_at": "2025-07-11T09:00:00Z",
                        "updated_at": "2025-07-11T10:30:00Z"
                    }
                ],
                "total_count": 4,
                "active_count": 3
            }
        }