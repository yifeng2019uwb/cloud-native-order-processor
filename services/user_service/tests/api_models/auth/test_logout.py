import pytest
from api_models.auth.logout import LogoutRequest, LogoutSuccessResponse, LogoutErrorResponse

def test_logout_request_serialization():
    req = LogoutRequest()
    data = req.model_dump()
    assert data == {}

def test_logout_success_response_serialization():
    resp = LogoutSuccessResponse()
    data = resp.model_dump()
    assert data["success"] is True
    assert data["message"] == "Logged out successfully"
    assert "timestamp" in data

def test_logout_error_response_serialization():
    resp = LogoutErrorResponse()
    data = resp.model_dump()
    assert data["success"] is False
    assert data["error"] == "LOGOUT_FAILED"
    assert data["message"] == "Logout failed. Please try again."
    assert "timestamp" in data
