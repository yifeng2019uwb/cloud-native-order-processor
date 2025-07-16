import pytest
from exceptions.secure_exceptions import StandardErrorResponse, SecureExceptionMapper
from exceptions.internal_exceptions import InternalAuthError
from datetime import datetime


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