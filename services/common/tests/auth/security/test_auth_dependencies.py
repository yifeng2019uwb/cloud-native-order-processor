"""
Unit tests for authentication dependencies

Tests the AuthenticatedUser model and get_current_user function.
"""

import os
import sys
from unittest.mock import Mock, patch
from datetime import datetime

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

# Add the common module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

# Import the actual classes and functions from source files
from src.auth.security.auth_dependencies import AuthenticatedUser, get_current_user
from src.auth.security.token_manager import TokenContext
from src.shared.constants.api_constants import HTTPStatus, ErrorMessages, RequestHeaders
from src.auth.security.jwt_constants import JwtFields, JWTConfig
from src.data.entities.user import DEFAULT_USER_ROLE


class TestAuthenticatedUser:
    """Test AuthenticatedUser model"""

    # Test constants
    TEST_USERNAME = "testuser123"
    TEST_ROLE = "customer"
    TEST_REQUEST_ID = "req-12345"
    TEST_ADMIN_ROLE = "admin"
    EMPTY_STRING = ""

    def test_authenticated_user_creation_with_required_fields(self):
        """Test AuthenticatedUser creation with required fields"""
        user = AuthenticatedUser(
            username=self.TEST_USERNAME,
            role=self.TEST_ROLE,
            request_id=self.TEST_REQUEST_ID
        )

        assert user.username == self.TEST_USERNAME
        assert user.role == self.TEST_ROLE
        assert user.request_id == self.TEST_REQUEST_ID

    def test_authenticated_user_creation_with_admin_role(self):
        """Test AuthenticatedUser creation with admin role"""
        user = AuthenticatedUser(
            username=self.TEST_USERNAME,
            role=self.TEST_ADMIN_ROLE,
            request_id=self.TEST_REQUEST_ID
        )

        assert user.username == self.TEST_USERNAME
        assert user.role == self.TEST_ADMIN_ROLE
        assert user.request_id == self.TEST_REQUEST_ID

    def test_authenticated_user_creation_missing_username(self):
        """Test AuthenticatedUser creation with missing username"""
        with pytest.raises(ValidationError):
            AuthenticatedUser(
                role=self.TEST_ROLE,
                request_id=self.TEST_REQUEST_ID
            )

    def test_authenticated_user_creation_missing_role(self):
        """Test AuthenticatedUser creation with missing role"""
        with pytest.raises(ValidationError):
            AuthenticatedUser(
                username=self.TEST_USERNAME,
                request_id=self.TEST_REQUEST_ID
            )

    def test_authenticated_user_creation_missing_request_id(self):
        """Test AuthenticatedUser creation with missing request_id"""
        with pytest.raises(ValidationError):
            AuthenticatedUser(
                username=self.TEST_USERNAME,
                role=self.TEST_ROLE
            )

    def test_authenticated_user_creation_empty_username(self):
        """Test AuthenticatedUser creation with empty username (should be allowed)"""
        user = AuthenticatedUser(
            username=self.EMPTY_STRING,
            role=self.TEST_ROLE,
            request_id=self.TEST_REQUEST_ID
        )

        assert user.username == self.EMPTY_STRING
        assert user.role == self.TEST_ROLE
        assert user.request_id == self.TEST_REQUEST_ID

    def test_authenticated_user_creation_empty_role(self):
        """Test AuthenticatedUser creation with empty role (should be allowed)"""
        user = AuthenticatedUser(
            username=self.TEST_USERNAME,
            role=self.EMPTY_STRING,
            request_id=self.TEST_REQUEST_ID
        )

        assert user.username == self.TEST_USERNAME
        assert user.role == self.EMPTY_STRING
        assert user.request_id == self.TEST_REQUEST_ID

    def test_authenticated_user_creation_empty_request_id(self):
        """Test AuthenticatedUser creation with empty request_id (should be allowed)"""
        user = AuthenticatedUser(
            username=self.TEST_USERNAME,
            role=self.TEST_ROLE,
            request_id=self.EMPTY_STRING
        )

        assert user.username == self.TEST_USERNAME
        assert user.role == self.TEST_ROLE
        assert user.request_id == self.EMPTY_STRING


class TestGetCurrentUser:
    """Test get_current_user function"""

    # Test constants
    TEST_USERNAME = "testuser123"
    TEST_ROLE = "customer"
    TEST_REQUEST_ID = "req-12345"
    TEST_TOKEN = "test-jwt-token"
    TEST_AUTH_HEADER = f"{JWTConfig.TOKEN_TYPE_BEARER.title()} {TEST_TOKEN}"
    TEST_USER_CONTEXT = TokenContext(
        username=TEST_USERNAME,
        role=TEST_ROLE,
        expiration=datetime.now(),
        issued_at=datetime.now(),
        issuer=None,
        audience=None,
        token_type=JWTConfig.ACCESS_TOKEN_TYPE,
        metadata={JwtFields.ROLE: TEST_ROLE}
    )

    # Mock path constants
    MOCK_TOKEN_MANAGER_PATH = 'src.auth.security.auth_dependencies.TokenManager'
    MOCK_GET_REQUEST_ID_PATH = 'src.auth.security.auth_dependencies.get_request_id_from_request'

    def test_get_current_user_success(self):
        """Test successful user authentication"""
        # Mock request with valid Authorization header
        mock_request = Mock()
        mock_request.headers = {
            RequestHeaders.AUTHORIZATION: self.TEST_AUTH_HEADER,
            RequestHeaders.REQUEST_ID: self.TEST_REQUEST_ID
        }

        with patch(self.MOCK_TOKEN_MANAGER_PATH) as mock_token_manager_class:
            mock_token_manager = Mock()
            mock_token_manager_class.return_value = mock_token_manager
            mock_token_manager.validate_token_comprehensive.return_value = self.TEST_USER_CONTEXT

            result = get_current_user(mock_request)

            assert isinstance(result, AuthenticatedUser)
            assert result.username == self.TEST_USERNAME
            assert result.role == self.TEST_ROLE
            assert result.request_id == self.TEST_REQUEST_ID

    def test_get_current_user_with_default_role(self):
        """Test user authentication with default role when role not in token"""
        # Mock request with valid Authorization header
        mock_request = Mock()
        mock_request.headers = {
            RequestHeaders.AUTHORIZATION: self.TEST_AUTH_HEADER,
            RequestHeaders.REQUEST_ID: self.TEST_REQUEST_ID
        }

        # User context without role (empty string)
        user_context_without_role = TokenContext(
            username=self.TEST_USERNAME,
            role="",
            expiration=datetime.now(),
            issued_at=datetime.now(),
            issuer=None,
            audience=None,
            token_type=JWTConfig.ACCESS_TOKEN_TYPE,
            metadata={}
        )

        with patch(self.MOCK_TOKEN_MANAGER_PATH) as mock_token_manager_class:
            mock_token_manager = Mock()
            mock_token_manager_class.return_value = mock_token_manager
            mock_token_manager.validate_token_comprehensive.return_value = user_context_without_role

            result = get_current_user(mock_request)

            assert isinstance(result, AuthenticatedUser)
            assert result.username == self.TEST_USERNAME
            assert result.role == DEFAULT_USER_ROLE
            assert result.request_id == self.TEST_REQUEST_ID

    def test_get_current_user_missing_authorization_header(self):
        """Test authentication with missing Authorization header"""
        mock_request = Mock()
        mock_request.headers = {}

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_request)

        assert exc_info.value.status_code == HTTPStatus.UNAUTHORIZED
        assert exc_info.value.detail == ErrorMessages.AUTHENTICATION_FAILED

    def test_get_current_user_none_authorization_header(self):
        """Test authentication with None Authorization header"""
        mock_request = Mock()
        mock_request.headers = {RequestHeaders.AUTHORIZATION: None}

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_request)

        assert exc_info.value.status_code == HTTPStatus.UNAUTHORIZED
        assert exc_info.value.detail == ErrorMessages.AUTHENTICATION_FAILED

    def test_get_current_user_invalid_authorization_header_format(self):
        """Test authentication with invalid Authorization header format"""
        mock_request = Mock()
        mock_request.headers = {RequestHeaders.AUTHORIZATION: "InvalidFormat"}

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_request)

        assert exc_info.value.status_code == HTTPStatus.UNAUTHORIZED
        assert exc_info.value.detail == ErrorMessages.AUTHENTICATION_FAILED

    def test_get_current_user_wrong_bearer_format(self):
        """Test authentication with wrong Bearer format"""
        mock_request = Mock()
        mock_request.headers = {RequestHeaders.AUTHORIZATION: "Basic token123"}

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_request)

        assert exc_info.value.status_code == HTTPStatus.UNAUTHORIZED
        assert exc_info.value.detail == ErrorMessages.AUTHENTICATION_FAILED

    def test_get_current_user_jwt_validation_failure(self):
        """Test authentication with JWT validation failure"""
        mock_request = Mock()
        mock_request.headers = {
            RequestHeaders.AUTHORIZATION: self.TEST_AUTH_HEADER,
            RequestHeaders.REQUEST_ID: self.TEST_REQUEST_ID
        }

        with patch(self.MOCK_TOKEN_MANAGER_PATH) as mock_token_manager_class:
            mock_token_manager = Mock()
            mock_token_manager_class.return_value = mock_token_manager
            mock_token_manager.validate_token_comprehensive.side_effect = Exception("Invalid token")

            with pytest.raises(HTTPException) as exc_info:
                get_current_user(mock_request)

            assert exc_info.value.status_code == HTTPStatus.UNAUTHORIZED
            assert exc_info.value.detail == ErrorMessages.AUTHENTICATION_FAILED

    def test_get_current_user_without_request_id_header(self):
        """Test authentication without X-Request-ID header (should generate one)"""
        mock_request = Mock()
        mock_request.headers = {RequestHeaders.AUTHORIZATION: self.TEST_AUTH_HEADER}

        with patch(self.MOCK_TOKEN_MANAGER_PATH) as mock_token_manager_class, \
             patch(self.MOCK_GET_REQUEST_ID_PATH) as mock_get_request_id:

            mock_token_manager = Mock()
            mock_token_manager_class.return_value = mock_token_manager
            mock_token_manager.validate_token_comprehensive.return_value = self.TEST_USER_CONTEXT
            mock_get_request_id.return_value = self.TEST_REQUEST_ID

            result = get_current_user(mock_request)

            assert isinstance(result, AuthenticatedUser)
            assert result.username == self.TEST_USERNAME
            assert result.role == self.TEST_ROLE
            assert result.request_id == self.TEST_REQUEST_ID
            mock_get_request_id.assert_called_once_with(mock_request)

    def test_get_current_user_token_extraction(self):
        """Test that token is correctly extracted from Authorization header"""
        mock_request = Mock()
        mock_request.headers = {
            RequestHeaders.AUTHORIZATION: self.TEST_AUTH_HEADER,
            RequestHeaders.REQUEST_ID: self.TEST_REQUEST_ID
        }

        with patch(self.MOCK_TOKEN_MANAGER_PATH) as mock_token_manager_class:
            mock_token_manager = Mock()
            mock_token_manager_class.return_value = mock_token_manager
            mock_token_manager.validate_token_comprehensive.return_value = self.TEST_USER_CONTEXT

            get_current_user(mock_request)

            # Verify that validate_token_comprehensive was called with the correct token
            mock_token_manager.validate_token_comprehensive.assert_called_once_with(self.TEST_TOKEN)
