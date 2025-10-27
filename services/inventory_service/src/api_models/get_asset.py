"""
Pydantic models specific to get asset API
"""
from pydantic import BaseModel, Field, field_validator

# Import centralized field validation functions
from validation.field_validators import validate_asset_id

ASSET_ID_FIELD = "asset_id"

# Import shared data models
from .shared.data_models import AssetDetailData


class GetAssetRequest(BaseModel):
    """Request model for GET /inventory/assets/{asset_id}"""

    asset_id: str = Field(..., description="Asset identifier (e.g., BTC, ETH)")

    @field_validator(ASSET_ID_FIELD)
    @classmethod
    def validate_asset_id_format(cls, v: str) -> str:
        """Layer 1: Basic format validation for asset_id"""
        return validate_asset_id(v)


class GetAssetResponse(BaseModel):
    """Response model for GET /inventory/assets/{asset_id}"""

    data: AssetDetailData
