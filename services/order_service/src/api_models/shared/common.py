"""
Shared Pydantic models used across all order service APIs
Path: services/order_service/src/api_models/shared/common.py
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class BaseResponse(BaseModel):
    """Base response model with common fields"""

    success: bool = Field(
        default=True,
        description="Operation success indicator"
    )

    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response timestamp"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SuccessResponse(BaseResponse):
    """Standard success response model"""

    message: str = Field(
        ...,
        max_length=200,
        description="Success message"
    )

    data: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional response data"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {},
                "timestamp": "2025-07-30T14:30:52Z"
            }
        }


class ErrorResponse(BaseResponse):
    """Standard error response model for client-facing errors"""

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

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "ORDER_NOT_FOUND",
                "message": "The requested order was not found",
                "details": None,
                "timestamp": "2025-07-30T14:30:52Z"
            }
        }


class ValidationErrorResponse(ErrorResponse):
    """Validation error response with field-specific details"""

    error: str = Field(
        default="VALIDATION_ERROR",
        description="Validation error code"
    )

    validation_errors: Optional[list] = Field(
        None,
        description="List of validation errors (generic, safe for client)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "VALIDATION_ERROR",
                "message": "The provided order data is invalid",
                "validation_errors": [
                    {
                        "field": "quantity",
                        "message": "Quantity must be greater than 0"
                    }
                ],
                "timestamp": "2025-07-30T14:30:52Z"
            }
        }
