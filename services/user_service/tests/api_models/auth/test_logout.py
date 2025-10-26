"""
Tests for logout API models - Focus on field validation
"""
import pytest
from pydantic import ValidationError
from api_models.auth.logout import LogoutRequest, LogoutResponse


def test_logout_request_valid():
    """Test valid LogoutRequest creation"""
    request = LogoutRequest()
    assert request is not None


def test_logout_response_valid():
    """Test valid LogoutResponse creation"""
    response = LogoutResponse()
    assert response.message == "Logged out successfully"


def test_logout_response_custom_message():
    """Test LogoutResponse with custom message"""
    custom_message = "Custom logout message"
    response = LogoutResponse(message=custom_message)
    assert response.message == custom_message