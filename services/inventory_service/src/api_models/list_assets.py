"""
Pydantic models specific to list assets API
"""
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

# Import centralized field validation functions
from validation.field_validators import validate_limit


LIMIT_FIELD = "limit"

# Import shared data models
from .shared.data_models import AssetData


class ListAssetsRequest(BaseModel):
    """Request model for GET /inventory/assets"""

    active_only: bool = Field(default=True, description="Filter by active status")
    limit: Optional[int] = Field(default=50, ge=1, le=250, description="Maximum number of assets to return")

    @field_validator(LIMIT_FIELD)
    @classmethod
    def validate_limit_format(cls, v: Optional[int]) -> Optional[int]:
        """Layer 1: Basic format validation for limit"""
        if v is not None:
            return validate_limit(v)
        return v


class ListAssetsResponse(BaseModel):
    """Response model for GET /inventory/assets"""

    data: List[AssetData]
    total_count: int
    active_count: int
