"""
Asset request models for inventory service API
Path: services/inventory-service/src/api_models/inventory/asset_requests.py
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict

# Import centralized validation functions
from validation.field_validators import validate_asset_id


class AssetIdRequest(BaseModel):
    """Request model for asset ID path parameter

    Layer 1: Field validation (format, sanitization) - handled by Pydantic @field_validator
    Layer 2: Business validation - handled by centralized functions in controllers
    """

    asset_id: str = Field(
        ...,
        description="Asset symbol/identifier (e.g., 'BTC', 'ETH')",
        example="BTC"
    )

    @field_validator('asset_id')
    @classmethod
    def validate_asset_id_field(cls, v: str) -> str:
        """Layer 1: Field validation for asset_id"""
        return validate_asset_id(v)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "asset_id": "BTC"
            }
        }
    )