"""
Shared Pydantic models used across all order service APIs
Path: services/order_service/src/api_models/shared/common.py
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime


class BaseResponse(BaseModel):
    """Base response model with common fields"""

    model_config = ConfigDict()

    success: bool = Field(
        default=True,
        description="Operation success indicator"
    )

    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response timestamp"
    )


class SuccessResponse(BaseResponse):
    """Standard success response model"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {},
                "timestamp": "2025-07-30T14:30:52Z"
            }
        }
    )

    message: str = Field(
        ...,
        max_length=200,
        description="Success message"
    )

    data: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional response data"
    )


class ErrorResponse(BaseResponse):
    """Standard error response model for client-facing errors"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": False,
                "error": "ORDER_NOT_FOUND",
                "message": "The requested order was not found",
                "details": None,
                "timestamp": "2025-07-30T14:30:52Z"
            }
        }
    )

    success: bool = Field(
        default=False,
        description="Operation success indicator"
    )

    error: str = Field(
        ...,
        max_length=50,
        description="Error code"
    )

    message: str = Field(
        ...,
        max_length=200,
        description="Human-readable error message"
    )

    details: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional error context (safe for client)"
    )


class ValidationErrorResponse(ErrorResponse):
    """Validation error response with field-specific details"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": False,
                "error": "VALIDATION_ERROR",
                "message": "Validation failed",
                "validation_errors": [
                    {
                        "field": "asset_id",
                        "message": "Asset ID cannot be empty"
                    }
                ],
                "timestamp": "2025-07-30T14:30:52Z"
            }
        }
    )

    error: str = Field(
        default="VALIDATION_ERROR",
        description="Validation error code"
    )

    validation_errors: Optional[list] = Field(
        None,
        description="List of field-specific validation errors"
    )
