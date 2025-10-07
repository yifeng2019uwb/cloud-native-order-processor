"""
Asset request models for inventory service API
Path: services/inventory-service/src/api_models/inventory/asset_requests.py
"""
from pydantic import BaseModel, Field, AfterValidator, ConfigDict
from typing import Annotated

# Import centralized validation functions
from validation.field_validators import validate_asset_id


def validate_asset_id_func(v: str) -> str:
    """Validation logic for asset_id field"""
    return validate_asset_id(v)


class AssetIdRequest(BaseModel):
    """Request model for asset ID path parameter

    Layer 1: Field validation (format, sanitization) - handled by AfterValidator
    Layer 2: Business validation - handled by centralized functions in controllers
    """

    asset_id: Annotated[str, AfterValidator(validate_asset_id_func)] = Field(
        ...,
        description="Asset symbol/identifier (e.g., 'BTC', 'ETH')",
        example="BTC"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "asset_id": "BTC"
            }
        }
    )