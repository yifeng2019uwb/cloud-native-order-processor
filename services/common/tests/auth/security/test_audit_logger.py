"""
Unit tests for AuditLogger class.
"""
# Standard library imports
from unittest.mock import patch, MagicMock

# Third-party imports
import pytest

# Local imports
from src.auth.security.audit_logger import AuditLogger
from src.shared.logging import LogActions


class TestAuditLogger:
    """Test cases for AuditLogger class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.audit_logger = AuditLogger()
        self.test_username = "testuser"
        self.test_ip = "192.168.1.1"
        self.test_user_agent = "Mozilla/5.0"

    @patch('src.auth.security.audit_logger.logger')
    def test_log_security_event_success(self, mock_logger):
        """Test successful security event logging."""
        event_type = LogActions.AUTH_SUCCESS
        details = {"reason": "successful authentication"}

        self.audit_logger.log_security_event(
            event_type,
            self.test_username,
            details,
            self.test_ip,
            self.test_user_agent
        )

        # Verify logger.info was called
        mock_logger.info.assert_called_once()
        call_kwargs = mock_logger.info.call_args[1]  # Get keyword arguments

        # Verify the call arguments
        assert call_kwargs['action'] == event_type
        assert call_kwargs['message'] == f"Security event: {event_type} for user {self.test_username}"
        assert call_kwargs['user'] == self.test_username

    @patch('src.auth.security.audit_logger.logger')
    def test_log_security_event_minimal(self, mock_logger):
        """Test security event logging with minimal parameters."""
        event_type = LogActions.SECURITY_EVENT

        self.audit_logger.log_security_event(event_type, self.test_username)

        # Verify logger.info was called
        mock_logger.info.assert_called_once()
        call_kwargs = mock_logger.info.call_args[1]  # Get keyword arguments

        # Verify the call arguments
        assert call_kwargs['action'] == event_type
        assert call_kwargs['message'] == f"Security event: {event_type} for user {self.test_username}"
        assert call_kwargs['user'] == self.test_username

    @patch('src.auth.security.audit_logger.logger')
    def test_log_login_success(self, mock_logger):
        """Test login success logging."""
        self.audit_logger.log_login_success(self.test_username, self.test_ip, self.test_user_agent)

        # Verify logger.info was called
        mock_logger.info.assert_called_once()
        call_kwargs = mock_logger.info.call_args[1]  # Get keyword arguments

        # Verify the call arguments
        assert call_kwargs['action'] == LogActions.AUTH_SUCCESS
        assert call_kwargs['message'] == f"Security event: {LogActions.AUTH_SUCCESS} for user {self.test_username}"
        assert call_kwargs['user'] == self.test_username

    @patch('src.auth.security.audit_logger.logger')
    def test_log_login_success_minimal(self, mock_logger):
        """Test login success logging with minimal parameters."""
        self.audit_logger.log_login_success(self.test_username)

        # Verify logger.info was called
        mock_logger.info.assert_called_once()
        call_kwargs = mock_logger.info.call_args[1]  # Get keyword arguments

        # Verify the call arguments
        assert call_kwargs['action'] == LogActions.AUTH_SUCCESS
        assert call_kwargs['message'] == f"Security event: {LogActions.AUTH_SUCCESS} for user {self.test_username}"
        assert call_kwargs['user'] == self.test_username

    @patch('src.auth.security.audit_logger.logger')
    def test_log_login_failure(self, mock_logger):
        """Test login failure logging."""
        reason = "Invalid credentials"
        self.audit_logger.log_login_failure(self.test_username, reason, self.test_ip, self.test_user_agent)

        # Verify logger.warning was called (login failure uses warning level)
        mock_logger.warning.assert_called_once()
        call_kwargs = mock_logger.warning.call_args[1]  # Get keyword arguments

        # Verify the call arguments
        assert call_kwargs['action'] == LogActions.AUTH_FAILED
        assert call_kwargs['message'] == f"Security warning: {LogActions.AUTH_FAILED} for user {self.test_username}"
        assert call_kwargs['user'] == self.test_username

    @patch('src.auth.security.audit_logger.logger')
    def test_log_logout(self, mock_logger):
        """Test logout logging."""
        self.audit_logger.log_logout(self.test_username, self.test_ip)

        # Verify logger.info was called
        mock_logger.info.assert_called_once()
        call_kwargs = mock_logger.info.call_args[1]  # Get keyword arguments

        # Verify the call arguments
        assert call_kwargs['action'] == LogActions.SECURITY_EVENT
        assert call_kwargs['message'] == f"Security event: {LogActions.SECURITY_EVENT} for user {self.test_username}"
        assert call_kwargs['user'] == self.test_username

    @patch('src.auth.security.audit_logger.logger')
    def test_log_password_change(self, mock_logger):
        """Test password change logging."""
        self.audit_logger.log_password_change(self.test_username, self.test_ip)

        # Verify logger.info was called
        mock_logger.info.assert_called_once()
        call_kwargs = mock_logger.info.call_args[1]  # Get keyword arguments

        # Verify the call arguments
        assert call_kwargs['action'] == LogActions.SECURITY_EVENT
        assert call_kwargs['message'] == f"Security event: {LogActions.SECURITY_EVENT} for user {self.test_username}"
        assert call_kwargs['user'] == self.test_username

    @patch('src.auth.security.audit_logger.logger')
    def test_log_token_created(self, mock_logger):
        """Test token creation logging."""
        self.audit_logger.log_token_created(self.test_username, "access_token", self.test_ip)

        # Verify logger.info was called
        mock_logger.info.assert_called_once()
        call_kwargs = mock_logger.info.call_args[1]  # Get keyword arguments

        # Verify the call arguments
        assert call_kwargs['action'] == LogActions.SECURITY_EVENT
        assert call_kwargs['message'] == f"Security event: {LogActions.SECURITY_EVENT} for user {self.test_username}"
        assert call_kwargs['user'] == self.test_username

    @patch('src.auth.security.audit_logger.logger')
    def test_log_access_denied(self, mock_logger):
        """Test access denied logging."""
        self.audit_logger.log_access_denied(self.test_username, "/admin/users", "Insufficient permissions", self.test_ip)

        # Verify logger.warning was called (access denied uses warning level)
        mock_logger.warning.assert_called_once()
        call_kwargs = mock_logger.warning.call_args[1]  # Get keyword arguments

        # Verify the call arguments
        assert call_kwargs['action'] == LogActions.ACCESS_DENIED
        assert call_kwargs['message'] == f"Security warning: {LogActions.ACCESS_DENIED} for user {self.test_username}"
        assert call_kwargs['user'] == self.test_username

    @patch('src.auth.security.audit_logger.logger')
    def test_info_level_events(self, mock_logger):
        """Test that certain events use info level."""
        info_events = [
            LogActions.AUTH_SUCCESS,
            LogActions.SECURITY_EVENT,
            LogActions.ACCESS_GRANTED
        ]

        for event_type in info_events:
            mock_logger.reset_mock()
            self.audit_logger.log_security_event(event_type, self.test_username)
            mock_logger.info.assert_called_once()

    @patch('src.auth.security.audit_logger.logger')
    def test_warning_level_events(self, mock_logger):
        """Test that certain events use warning level."""
        warning_events = [
            LogActions.AUTH_FAILED,
            LogActions.ACCESS_DENIED
        ]

        for event_type in warning_events:
            mock_logger.reset_mock()
            details = {"reason": "test"} if event_type == LogActions.AUTH_FAILED else {"resource": "test", "reason": "test"}
            self.audit_logger.log_security_event(event_type, self.test_username, details)
            mock_logger.warning.assert_called_once()

    @patch('src.auth.security.audit_logger.logger')
    def test_unknown_event_defaults_to_info(self, mock_logger):
        """Test that unknown events default to info level."""
        # Test with a custom event type that's not in the predefined lists
        self.audit_logger.log_security_event("custom_event", self.test_username)
        mock_logger.info.assert_called_once()

    def test_security_event_type_values(self):
        """Test that LogActions enum has expected values."""
        assert LogActions.AUTH_SUCCESS == "auth_success"
        assert LogActions.AUTH_FAILED == "auth_failed"
        assert LogActions.ACCESS_GRANTED == "access_granted"
        assert LogActions.ACCESS_DENIED == "access_denied"
        assert LogActions.SECURITY_EVENT == "security_event"