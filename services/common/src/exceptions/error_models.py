"""
Standardized error response models for all services
Path: services/common/src/exceptions/error_models.py
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from .error_codes import CommonErrorCode, get_http_status_code


class ValidationError(BaseModel):
    """Individual validation error for a field"""
    field: str = Field(..., description="Field name that failed validation")
    message: str = Field(..., description="Human-readable error message")
    value: Optional[Any] = Field(None, description="Invalid value that caused the error")


class ErrorDetails(BaseModel):
    """Additional error context and details"""
    validation_errors: Optional[List[ValidationError]] = Field(
        None, description="Field-specific validation errors"
    )
    field: Optional[str] = Field(None, description="Specific field that caused the error")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional error context")
    request_id: Optional[str] = Field(None, description="Request ID for tracing")


class ErrorResponse(BaseModel):
    """Standardized error response for all services"""
    success: bool = Field(False, description="Operation success indicator")
    error_code: str = Field(..., description="Standard error code")
    message: str = Field(..., description="Human-readable error message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    details: Optional[ErrorDetails] = Field(None, description="Additional error details")
    request_id: Optional[str] = Field(None, description="Request ID for tracing")

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error_code": "VALIDATION_ERROR",
                "message": "Please correct the following errors",
                "timestamp": "2025-07-30T17:03:17.267111Z",
                "details": {
                    "validation_errors": [
                        {
                            "field": "email",
                            "message": "Invalid email format",
                            "value": "invalid-email"
                        }
                    ]
                },
                "request_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


def create_error_response(
    error_code: CommonErrorCode,
    message: str,
    details: Optional[ErrorDetails] = None,
    request_id: Optional[str] = None
) -> ErrorResponse:
    """Create a standardized error response"""
    return ErrorResponse(
        success=False,
        error_code=error_code.value,
        message=message,
        timestamp=datetime.utcnow(),
        details=details,
        request_id=request_id
    )


def create_validation_error_response(
    validation_errors: List[ValidationError],
    message: str = "Please correct the following errors",
    request_id: Optional[str] = None
) -> ErrorResponse:
    """Create a validation error response"""
    details = ErrorDetails(validation_errors=validation_errors)
    return create_error_response(
        error_code=CommonErrorCode.VALIDATION_ERROR,
        message=message,
        details=details,
        request_id=request_id
    )


def create_resource_not_found_response(
    resource_type: str,
    resource_id: Optional[str] = None,
    request_id: Optional[str] = None
) -> ErrorResponse:
    """Create a resource not found error response"""
    if resource_id:
        message = f"{resource_type} '{resource_id}' not found"
    else:
        message = f"{resource_type} not found"

    details = ErrorDetails(
        field="id",
        context={"resource_type": resource_type, "resource_id": resource_id}
    )

    return create_error_response(
        error_code=CommonErrorCode.RESOURCE_NOT_FOUND,
        message=message,
        details=details,
        request_id=request_id
    )


def create_resource_exists_response(
    resource_type: str,
    resource_id: Optional[str] = None,
    field: Optional[str] = None,
    request_id: Optional[str] = None
) -> ErrorResponse:
    """Create a resource exists error response"""
    if resource_id:
        message = f"{resource_type} '{resource_id}' already exists"
    else:
        message = f"{resource_type} already exists"

    details = ErrorDetails(
        field=field,
        context={"resource_type": resource_type, "resource_id": resource_id}
    )

    return create_error_response(
        error_code=CommonErrorCode.RESOURCE_EXISTS,
        message=message,
        details=details,
        request_id=request_id
    )


def create_authentication_failed_response(
    message: str = "Authentication failed. Please check your credentials.",
    request_id: Optional[str] = None
) -> ErrorResponse:
    """Create an authentication failed error response"""
    return create_error_response(
        error_code=CommonErrorCode.AUTHENTICATION_FAILED,
        message=message,
        request_id=request_id
    )


def create_internal_error_response(
    message: str = "An internal error occurred. Please try again later.",
    request_id: Optional[str] = None
) -> ErrorResponse:
    """Create an internal error response"""
    return create_error_response(
        error_code=CommonErrorCode.INTERNAL_ERROR,
        message=message,
        request_id=request_id
    )