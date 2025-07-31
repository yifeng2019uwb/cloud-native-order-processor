from api_models.shared.common import (
    BaseResponse,
    SuccessResponse,
    TokenResponse,
    UserBaseInfo,
    ErrorResponse,
    ValidationErrorResponse
)
from datetime import datetime, date

def test_base_response_serialization():
    resp = BaseResponse()
    data = resp.model_dump()
    assert data["success"] is True
    assert "timestamp" in data

def test_success_response_serialization():
    resp = SuccessResponse(message="OK", data={"foo": "bar"})
    data = resp.model_dump()
    assert data["success"] is True
    assert data["message"] == "OK"
    assert data["data"] == {"foo": "bar"}
    assert "timestamp" in data

def test_token_response_serialization():
    resp = TokenResponse(access_token="token123", token_type="bearer", expires_in=3600)
    data = resp.model_dump()
    assert data["access_token"] == "token123"
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == 3600

def test_user_base_info_serialization():
    resp = UserBaseInfo(
        username="john_doe123",
        email="john.doe@example.com",
        first_name="John",
        last_name="Doe",
        marketing_emails_consent=False,
        created_at=datetime(2025, 7, 9, 10, 30, 0),
        updated_at=datetime(2025, 7, 9, 10, 30, 0)
    )
    data = resp.model_dump()
    assert data["username"] == "john_doe123"
    assert data["email"] == "john.doe@example.com"
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert data["marketing_emails_consent"] is False
    # Handle datetime object returned by Pydantic
    assert isinstance(data["created_at"], (str, datetime))
    assert isinstance(data["updated_at"], (str, datetime))

def test_error_response_serialization():
    resp = ErrorResponse(
        success=False,
        error="INVALID_INPUT",
        message="The provided information is invalid",
        details={"field": "email"}
    )
    data = resp.model_dump()
    assert data["success"] is False
    assert data["error"] == "INVALID_INPUT"
    assert data["message"] == "The provided information is invalid"
    assert data["details"] == {"field": "email"}
    assert "timestamp" in data

def test_validation_error_response_serialization():
    resp = ValidationErrorResponse(
        success=False,
        error="VALIDATION_ERROR",
        message="The provided data is invalid",
        validation_errors=[{"field": "email", "message": "Please enter a valid email address"}]
    )
    data = resp.model_dump()
    assert data["success"] is False
    assert data["error"] == "VALIDATION_ERROR"
    assert data["message"] == "The provided data is invalid"
    assert data["validation_errors"] == [{"field": "email", "message": "Please enter a valid email address"}]
    assert "timestamp" in data