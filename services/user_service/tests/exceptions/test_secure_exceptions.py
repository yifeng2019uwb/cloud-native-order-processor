import pytest
from exceptions.secure_exceptions import StandardErrorResponse, SecureExceptionMapper
from exceptions.internal_exceptions import InternalAuthError
from datetime import datetime
from fastapi import status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from unittest.mock import MagicMock, patch
import asyncio
import uuid
from src.exceptions.secure_exceptions import (
    secure_internal_exception_handler,
    secure_validation_exception_handler,
    secure_general_exception_handler
)
import traceback


class TestSecureExceptions:
    """Test secure exception handling"""

    def test_standard_error_response_validation_error(self):
        """Test validation error response creation"""
        response = StandardErrorResponse.validation_error()

        assert response["success"] is False
        assert response["error"] == "INVALID_INPUT"
        assert "message" in response
        assert "timestamp" in response

    def test_standard_error_response_user_exists_error(self):
        """Test user exists error response creation"""
        response = StandardErrorResponse.user_exists_error("username")

        assert response["success"] is False
        assert response["error"] == "USER_EXISTS"
        assert "Username already exists" in response["message"]
        assert "timestamp" in response

    def test_standard_error_response_authentication_failed(self):
        """Test authentication failed response creation"""
        response = StandardErrorResponse.authentication_failed()

        assert response["success"] is False
        assert response["error"] == "AUTHENTICATION_FAILED"
        assert "Invalid credentials" in response["message"]
        assert "timestamp" in response

    def test_standard_error_response_service_unavailable(self):
        """Test service unavailable response creation"""
        response = StandardErrorResponse.service_unavailable()

        assert response["success"] is False
        assert response["error"] == "SERVICE_UNAVAILABLE"
        assert "Service is temporarily unavailable" in response["message"]
        assert "timestamp" in response

    def test_secure_exception_mapper_known_error(self):
        """Test mapping known internal error to client response"""
        internal_error = InternalAuthError(
            error_code="USER_EXISTS_DETAILED",
            message="User already exists",
            context={"username": "testuser"}
        )

        status_code, response = SecureExceptionMapper.map_to_client_response(internal_error)

        assert status_code == 409  # HTTP_409_CONFLICT
        assert response["success"] is False
        assert response["error"] == "REGISTRATION_FAILED"

    def test_secure_exception_mapper_unknown_error(self):
        """Test mapping unknown internal error to generic response"""
        internal_error = InternalAuthError(
            error_code="UNKNOWN_ERROR",
            message="Some unknown error",
            context={}
        )

        status_code, response = SecureExceptionMapper.map_to_client_response(internal_error)

        assert status_code == 500  # HTTP_500_INTERNAL_SERVER_ERROR
        assert response["success"] is False
        assert response["error"] == "INTERNAL_ERROR"

# --- Additional StandardErrorResponse tests ---
def test_standard_error_response_rate_limited():
    resp = StandardErrorResponse.rate_limited()
    assert resp["error"] == "TOO_MANY_REQUESTS"
    assert resp["success"] is False
    assert "Too many requests" in resp["message"]
    assert "timestamp" in resp

def test_standard_error_response_internal_error():
    resp = StandardErrorResponse.internal_error()
    assert resp["error"] == "INTERNAL_ERROR"
    assert resp["success"] is False
    assert "unexpected error" in resp["message"].lower()
    assert "timestamp" in resp

def test_standard_error_response_user_exists_error_no_field():
    resp = StandardErrorResponse.user_exists_error()
    assert resp["error"] == "REGISTRATION_FAILED"
    assert resp["success"] is False
    assert "Unable to create account" in resp["message"]
    assert "timestamp" in resp

def test_standard_error_response_validation_error_with_fields():
    errors = [{"field": "username", "message": "too short"}]
    resp = StandardErrorResponse.validation_error(errors)
    assert resp["error"] == "VALIDATION_ERROR"
    assert resp["success"] is False
    assert resp["validation_errors"] == errors
    assert "timestamp" in resp

# --- Additional SecureExceptionMapper tests ---
def make_internal_error(code):
    return InternalAuthError(
        error_code=code,
        message="msg",
        context={}
    )

def test_secure_exception_mapper_database_error():
    err = make_internal_error("DATABASE_ERROR_DETAILED")
    status_code, resp = SecureExceptionMapper.map_to_client_response(err)
    assert status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert resp["error"] == "SERVICE_UNAVAILABLE"

def test_secure_exception_mapper_validation_error():
    err = make_internal_error("VALIDATION_ERROR_DETAILED")
    status_code, resp = SecureExceptionMapper.map_to_client_response(err)
    assert status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert resp["error"] == "INVALID_INPUT"

def test_secure_exception_mapper_security_violation():
    err = make_internal_error("SECURITY_VIOLATION_DETAILED")
    status_code, resp = SecureExceptionMapper.map_to_client_response(err)
    assert status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert resp["error"] == "TOO_MANY_REQUESTS"

def test_secure_exception_mapper_unknown_code():
    err = make_internal_error("SOMETHING_UNKNOWN")
    status_code, resp = SecureExceptionMapper.map_to_client_response(err)
    assert status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert resp["error"] == "INTERNAL_ERROR"

# --- Exception handler tests ---
@pytest.mark.asyncio
def test_secure_internal_exception_handler():
    req = MagicMock()
    req.method = "POST"
    req.url = "http://test/register"
    req.client = MagicMock(host="1.2.3.4")
    req.headers = {"user-agent": "pytest"}
    exc = InternalAuthError(
        error_code="USER_EXISTS_DETAILED",
        message="User already exists",
        context={"username": "testuser"}
    )
    resp = asyncio.run(secure_internal_exception_handler(req, exc))
    assert isinstance(resp, JSONResponse)
    assert resp.status_code == 409
    assert resp.body

# --- secure_validation_exception_handler mapping branches ---
def make_validation_error(loc, msg):
    return {"loc": loc, "msg": msg, "type": "value_error"}

@pytest.mark.asyncio
def test_secure_validation_exception_handler_min_length_username():
    req = MagicMock()
    req.method = "POST"
    req.url = "http://test/register"
    req.client = MagicMock(host="1.2.3.4")
    exc = RequestValidationError([
        make_validation_error(["body", "username"], "ensure this value has at least 6 characters")
    ])
    resp = asyncio.run(secure_validation_exception_handler(req, exc))
    assert b"Username must be at least 6 characters" in resp.body

@pytest.mark.asyncio
def test_secure_validation_exception_handler_max_length_password():
    req = MagicMock()
    req.method = "POST"
    req.url = "http://test/register"
    req.client = MagicMock(host="1.2.3.4")
    exc = RequestValidationError([
        make_validation_error(["body", "password"], "ensure this value has at most 20 characters")
    ])
    resp = asyncio.run(secure_validation_exception_handler(req, exc))
    assert b"Password must be no more than 20 characters" in resp.body

@pytest.mark.asyncio
def test_secure_validation_exception_handler_invalid_email():
    req = MagicMock()
    req.method = "POST"
    req.url = "http://test/register"
    req.client = MagicMock(host="1.2.3.4")
    exc = RequestValidationError([
        make_validation_error(["body", "email"], "value is not a valid email address")
    ])
    resp = asyncio.run(secure_validation_exception_handler(req, exc))
    assert b"Please enter a valid email address" in resp.body

@pytest.mark.asyncio
def test_secure_validation_exception_handler_regex_username():
    req = MagicMock()
    req.method = "POST"
    req.url = "http://test/register"
    req.client = MagicMock(host="1.2.3.4")
    exc = RequestValidationError([
        make_validation_error(["body", "username"], "ensure this value matches some pattern")
    ])
    resp = asyncio.run(secure_validation_exception_handler(req, exc))
    assert b"Username can only contain letters, numbers, and underscores" in resp.body

@pytest.mark.asyncio
def test_secure_validation_exception_handler_contains_password_uppercase():
    req = MagicMock()
    req.method = "POST"
    req.url = "http://test/register"
    req.client = MagicMock(host="1.2.3.4")
    exc = RequestValidationError([
        make_validation_error(["body", "password"], "ensure this value contains uppercase")
    ])
    resp = asyncio.run(secure_validation_exception_handler(req, exc))
    assert b"Password must contain at least one uppercase letter" in resp.body

@pytest.mark.asyncio
def test_secure_validation_exception_handler_unknown_field():
    req = MagicMock()
    req.method = "POST"
    req.url = "http://test/register"
    req.client = MagicMock(host="1.2.3.4")
    exc = RequestValidationError([
        make_validation_error(["body", "custom_field"], "some unknown error")
    ])
    resp = asyncio.run(secure_validation_exception_handler(req, exc))
    assert b"custom_field" in resp.body
    assert b"some unknown error" in resp.body

@pytest.mark.asyncio
def test_secure_validation_exception_handler_empty_loc():
    req = MagicMock()
    req.method = "POST"
    req.url = "http://test/register"
    req.client = MagicMock(host="1.2.3.4")
    exc = RequestValidationError([
        make_validation_error([], "some error with no loc")
    ])
    resp = asyncio.run(secure_validation_exception_handler(req, exc))
    assert b"unknown" in resp.body
    assert b"some error with no loc" in resp.body

@pytest.mark.asyncio
def test_secure_validation_exception_handler_first_name_min_length():
    req = MagicMock()
    req.method = "POST"
    req.url = "http://test/register"
    req.client = MagicMock(host="1.2.3.4")
    exc = RequestValidationError([
        {"loc": ["body", "first_name"], "msg": "ensure this value has at least 1 characters", "type": "value_error"}
    ])
    resp = asyncio.run(secure_validation_exception_handler(req, exc))
    assert b"First Name must be at least 1 character" in resp.body

@pytest.mark.asyncio
def test_secure_validation_exception_handler_last_name_min_length():
    req = MagicMock()
    req.method = "POST"
    req.url = "http://test/register"
    req.client = MagicMock(host="1.2.3.4")
    exc = RequestValidationError([
        {"loc": ["body", "last_name"], "msg": "ensure this value has at least 1 characters", "type": "value_error"}
    ])
    resp = asyncio.run(secure_validation_exception_handler(req, exc))
    assert b"Last Name must be at least 1 character" in resp.body

@pytest.mark.asyncio
def test_secure_validation_exception_handler_password_min_length():
    req = MagicMock()
    req.method = "POST"
    req.url = "http://test/register"
    req.client = MagicMock(host="1.2.3.4")
    exc = RequestValidationError([
        {"loc": ["body", "password"], "msg": "ensure this value has at least 12 characters", "type": "value_error"}
    ])
    resp = asyncio.run(secure_validation_exception_handler(req, exc))
    assert b"Password must be at least 12 characters" in resp.body

@pytest.mark.asyncio
def test_secure_validation_exception_handler_password_regex():
    req = MagicMock()
    req.method = "POST"
    req.url = "http://test/register"
    req.client = MagicMock(host="1.2.3.4")
    exc = RequestValidationError([
        {"loc": ["body", "password"], "msg": "ensure this value matches some pattern", "type": "value_error"}
    ])
    resp = asyncio.run(secure_validation_exception_handler(req, exc))
    assert b"Password must contain uppercase, lowercase, numbers, and special characters" in resp.body

@pytest.mark.asyncio
def test_secure_validation_exception_handler_password_contains_lowercase():
    req = MagicMock()
    req.method = "POST"
    req.url = "http://test/register"
    req.client = MagicMock(host="1.2.3.4")
    exc = RequestValidationError([
        {"loc": ["body", "password"], "msg": "ensure this value contains lowercase", "type": "value_error"}
    ])
    resp = asyncio.run(secure_validation_exception_handler(req, exc))
    assert b"Password must contain at least one lowercase letter" in resp.body

@pytest.mark.asyncio
def test_secure_validation_exception_handler_password_contains_number():
    req = MagicMock()
    req.method = "POST"
    req.url = "http://test/register"
    req.client = MagicMock(host="1.2.3.4")
    exc = RequestValidationError([
        {"loc": ["body", "password"], "msg": "ensure this value contains number", "type": "value_error"}
    ])
    resp = asyncio.run(secure_validation_exception_handler(req, exc))
    assert b"Password must contain at least one number" in resp.body

@pytest.mark.asyncio
def test_secure_validation_exception_handler_password_contains_special():
    req = MagicMock()
    req.method = "POST"
    req.url = "http://test/register"
    req.client = MagicMock(host="1.2.3.4")
    exc = RequestValidationError([
        {"loc": ["body", "password"], "msg": "ensure this value contains special character", "type": "value_error"}
    ])
    resp = asyncio.run(secure_validation_exception_handler(req, exc))
    assert b"Password must contain at least one special character" in resp.body

# --- logger and traceback coverage ---
@pytest.mark.asyncio
def test_secure_validation_exception_handler_logs_warning():
    req = MagicMock()
    req.method = "POST"
    req.url = "http://test/register"
    req.client = None
    exc = RequestValidationError([
        {"loc": ["body", "username"], "msg": "ensure this value has at least 6 characters", "type": "value_error"}
    ])
    with patch("src.exceptions.secure_exceptions.logger.warning") as mock_warn:
        resp = asyncio.run(secure_validation_exception_handler(req, exc))
        assert mock_warn.called
        # Should log client_ip as 'unknown'
        args, kwargs = mock_warn.call_args
        assert "client_ip" in kwargs["extra"]
        assert kwargs["extra"]["client_ip"] == "unknown"


# --- secure_general_exception_handler branches ---
@pytest.mark.asyncio
def test_secure_general_exception_handler_with_client():
    req = MagicMock()
    req.method = "GET"
    req.url = "http://test/profile"
    req.client = MagicMock(host="1.2.3.4")
    exc = RuntimeError("fail")
    resp = asyncio.run(secure_general_exception_handler(req, exc))
    assert resp.status_code == 500
    assert b"INTERNAL_ERROR" in resp.body

@pytest.mark.asyncio
def test_secure_general_exception_handler_no_client():
    req = MagicMock()
    req.method = "GET"
    req.url = "http://test/profile"
    req.client = None
    exc = Exception("fail")
    resp = asyncio.run(secure_general_exception_handler(req, exc))
    assert resp.status_code == 500
    assert b"INTERNAL_ERROR" in resp.body

# --- Edge: unknown error type for logging ---
@pytest.mark.asyncio
def test_secure_general_exception_handler_custom_exception():
    class CustomError(Exception):
        pass
    req = MagicMock()
    req.method = "GET"
    req.url = "http://test/profile"
    req.client = MagicMock(host="1.2.3.4")
    exc = CustomError("fail-custom")
    resp = asyncio.run(secure_general_exception_handler(req, exc))
    assert resp.status_code == 500
    assert b"INTERNAL_ERROR" in resp.body

# --- Edge case: validation_error with empty list ---
def test_standard_error_response_validation_error_empty_list():
    resp = StandardErrorResponse.validation_error([])
    assert resp["error"] == "INVALID_INPUT"
    assert resp["success"] is False
    assert "timestamp" in resp

# --- logger and traceback coverage ---
def test_secure_general_exception_handler_logs_error_and_traceback():
    req = MagicMock()
    req.method = "GET"
    req.url = "http://test/profile"
    req.client = None
    exc = Exception("fail")
    with patch("src.exceptions.secure_exceptions.logger.error") as mock_error, \
         patch("src.exceptions.secure_exceptions.traceback.format_exc", return_value="fake-traceback") as mock_tb:
        resp = asyncio.run(secure_general_exception_handler(req, exc))
        assert mock_error.called
        args, kwargs = mock_error.call_args
        assert "traceback" in kwargs["extra"]
        assert kwargs["extra"]["traceback"] == "fake-traceback"
        assert "client_ip" in kwargs["extra"]
        assert kwargs["extra"]["client_ip"] == "unknown"