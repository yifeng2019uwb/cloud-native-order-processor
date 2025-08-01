import pytest
from pydantic import ValidationError
from api_models.auth.login import UserLoginRequest, LoginSuccessResponse, LoginErrorResponse
from api_models.shared.common import UserBaseInfo
from datetime import datetime, date

# --- UserLoginRequest: Valid data ---
def test_user_login_request_valid():
    req = UserLoginRequest(
        username="john_doe123",
        password="SecurePassword123!"
    )
    assert req.username == "john_doe123"
    assert req.password == "SecurePassword123!"

# --- Username validation ---
def test_user_login_request_username_too_short():
    with pytest.raises(ValidationError):
        UserLoginRequest(username="abc", password="SecurePassword123!")

def test_user_login_request_username_too_long():
    with pytest.raises(ValidationError):
        UserLoginRequest(username="a"*31, password="SecurePassword123!")

def test_user_login_request_username_whitespace_trimming():
    req = UserLoginRequest(username="  john_doe123  ", password="SecurePassword123!")
    assert req.username.strip() == "john_doe123"

# --- Password validation ---
def test_user_login_request_password_too_short():
    with pytest.raises(ValidationError):
        UserLoginRequest(username="john_doe123", password="short")

def test_user_login_request_password_too_long():
    with pytest.raises(ValidationError):
        UserLoginRequest(username="john_doe123", password="a"*21)

# --- LoginSuccessResponse serialization ---
def test_login_success_response_serialization():
    from api_models.auth.login import UserLoginResponse

    login_data = UserLoginResponse(
        access_token="token123",
        token_type="bearer",
        expires_in=86400
    )

    resp = LoginSuccessResponse(
        message="Login successful",
        data=login_data
    )
    data = resp.model_dump()
    assert data["message"] == "Login successful"
    assert data["data"]["access_token"] == "token123"
    assert data["data"]["token_type"] == "bearer"
    assert data["data"]["expires_in"] == 86400

# --- LoginErrorResponse serialization ---
def test_login_error_response_serialization():
    resp = LoginErrorResponse(
        success=False,
        error="AUTHENTICATION_FAILED",
        message="Invalid credentials. Please check your username and password.",
        details=None
    )
    data = resp.model_dump()
    assert data["success"] is False
    assert data["error"] == "AUTHENTICATION_FAILED"
    assert data["message"] == "Invalid credentials. Please check your username and password."
    assert data["details"] is None
