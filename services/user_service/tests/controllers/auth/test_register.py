"""
Tests for register controller - Focus on business logic
"""
import pytest
import pydantic
from fastapi import HTTPException, status
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import date, timedelta
from controllers.auth.register import register_user
from api_models.auth.registration import UserRegistrationRequest, RegistrationResponse
from user_exceptions import CNOPUserAlreadyExistsException, CNOPUserValidationException
from common.exceptions.shared_exceptions import (
    CNOPEntityAlreadyExistsException,
    CNOPInternalServerException
)
from tests.utils.dependency_constants import AUDIT_LOGGER_CLASS


# Test constants
TEST_IP_ADDRESS = "127.0.0.1"
TEST_USER_AGENT = "pytest"
TEST_REQUEST_ID = "test-request-id"
TEST_USERNAME_NEW = "newuser"
TEST_USERNAME_EXISTING = "existinguser"
TEST_EMAIL_NEW = "newuser@example.com"
TEST_EMAIL_EXISTING = "existing@example.com"
TEST_PASSWORD = "ValidPass123!@#"
TEST_FIRST_NAME = "New"
TEST_LAST_NAME = "User"

def create_mock_request(request_id=TEST_REQUEST_ID):
    """Helper function to create a mock request object with headers"""
    mock_request = MagicMock()
    mock_request.client = MagicMock()
    mock_request.client.host = TEST_IP_ADDRESS
    mock_request.headers = {"X-Request-ID": request_id, "user-agent": TEST_USER_AGENT}
    return mock_request


def test_register_success():
    """Test successful user registration"""
    mock_user_dao = MagicMock()
    mock_user_dao.get_user_by_username = MagicMock(return_value=None)
    mock_user_dao.get_user_by_email = MagicMock(return_value=None)
    mock_user = MagicMock()
    mock_user.username = TEST_USERNAME_NEW
    mock_user_dao.create_user = MagicMock(return_value=mock_user)

    # Mock balance_dao
    mock_balance_dao = MagicMock()
    mock_balance_dao.create_balance = MagicMock()

    mock_request = MagicMock()
    mock_request.client = MagicMock(host=TEST_IP_ADDRESS)
    mock_request.headers = {"user-agent": TEST_USER_AGENT}

    reg_data = UserRegistrationRequest(
        username=TEST_USERNAME_NEW,
        email=TEST_EMAIL_NEW,
        password=TEST_PASSWORD,
        first_name=TEST_FIRST_NAME,
        last_name=TEST_LAST_NAME,
        phone="+1-555-123-4567"
    )

    # Call the function
    result = register_user(
        reg_data,
        request=mock_request,
        user_dao=mock_user_dao,
        balance_dao=mock_balance_dao
    )

    # Verify result
    assert isinstance(result, RegistrationResponse)
    assert result.message == "User registered successfully"


@patch(AUDIT_LOGGER_CLASS)
def test_register_username_already_exists(mock_audit_logger_class):
    """Test registration with existing username"""
    mock_user_dao = MagicMock()
    mock_existing_user = MagicMock()
    mock_existing_user.username = TEST_USERNAME_EXISTING
    mock_user_dao.get_user_by_username.return_value = mock_existing_user

    reg_data = UserRegistrationRequest(
        username=TEST_USERNAME_EXISTING,
        email=TEST_EMAIL_NEW,
        password=TEST_PASSWORD,
        first_name=TEST_FIRST_NAME,
        last_name=TEST_LAST_NAME
    )

    # Call the function and expect exception
    with pytest.raises(CNOPUserAlreadyExistsException):
        register_user(
            reg_data,
            request=create_mock_request(),
            user_dao=mock_user_dao,
            balance_dao=MagicMock()
        )


@patch(AUDIT_LOGGER_CLASS)
def test_register_email_already_exists(mock_audit_logger_class):
    """Test registration with existing email"""
    mock_user_dao = MagicMock()
    mock_user_dao.get_user_by_username.return_value = None
    mock_existing_user = MagicMock()
    mock_existing_user.email = TEST_EMAIL_EXISTING
    mock_user_dao.get_user_by_email.return_value = mock_existing_user

    reg_data = UserRegistrationRequest(
        username=TEST_USERNAME_NEW,
        email=TEST_EMAIL_EXISTING,
        password=TEST_PASSWORD,
        first_name=TEST_FIRST_NAME,
        last_name=TEST_LAST_NAME
    )

    # Call the function and expect exception
    with pytest.raises(CNOPUserAlreadyExistsException):
        register_user(
            reg_data,
            request=create_mock_request(),
            user_dao=mock_user_dao,
            balance_dao=MagicMock()
        )


@patch(AUDIT_LOGGER_CLASS)
def test_register_validation_error(mock_audit_logger_class):
    """Test registration with validation error"""
    mock_user_dao = MagicMock()
    mock_user_dao.get_user_by_username.return_value = None
    mock_user_dao.get_user_by_email.return_value = None
    mock_user_dao.create_user.side_effect = CNOPUserValidationException("Validation failed")

    reg_data = UserRegistrationRequest(
        username=TEST_USERNAME_NEW,
        email=TEST_EMAIL_NEW,
        password=TEST_PASSWORD,
        first_name=TEST_FIRST_NAME,
        last_name=TEST_LAST_NAME
    )

    # Call the function and expect exception
    with pytest.raises(CNOPUserValidationException):
        register_user(
            reg_data,
            request=create_mock_request(),
            user_dao=mock_user_dao,
            balance_dao=MagicMock()
        )