"""
Unit tests for AuditLogger class.
"""
import pytest
from unittest.mock import patch, MagicMock
from src.auth.security.audit_logger import AuditLogger, SecurityEventType


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
        event_type = SecurityEventType.LOGIN_SUCCESS
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
        call_args = mock_logger.info.call_args[0][0]

        # Verify message contains expected elements
        assert "SECURITY_AUDIT: login_success" in call_args
        assert f"User: {self.test_username}" in call_args
        assert f"IP: {self.test_ip}" in call_args
        assert "Details: {'reason': 'successful authentication'}" in call_args

    @patch('src.auth.security.audit_logger.logger')
    def test_log_security_event_minimal(self, mock_logger):
        """Test security event logging with minimal parameters."""
        event_type = SecurityEventType.LOGOUT

        self.audit_logger.log_security_event(event_type, self.test_username)

        # Verify logger.info was called
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]

        # Verify message contains expected elements
        assert "SECURITY_AUDIT: logout" in call_args
        assert f"User: {self.test_username}" in call_args
        assert "IP:" not in call_args  # Should not be present
        assert "Details:" not in call_args  # Should not be present

    @patch('src.auth.security.audit_logger.logger')
    def test_log_login_success(self, mock_logger):
        """Test login success logging."""
        self.audit_logger.log_login_success(self.test_username, self.test_ip, self.test_user_agent)

        # Verify logger.info was called
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]

        # Verify message contains expected elements
        assert "SECURITY_AUDIT: login_success" in call_args
        assert f"User: {self.test_username}" in call_args
        assert f"IP: {self.test_ip}" in call_args

    @patch('src.auth.security.audit_logger.logger')
    def test_log_login_success_minimal(self, mock_logger):
        """Test login success logging with minimal parameters."""
        self.audit_logger.log_login_success(self.test_username)

        # Verify logger.info was called
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]

        # Verify message contains expected elements
        assert "SECURITY_AUDIT: login_success" in call_args
        assert f"User: {self.test_username}" in call_args
        assert "IP:" not in call_args  # Should not be present

    @patch('src.auth.security.audit_logger.logger')
    def test_log_login_failure(self, mock_logger):
        """Test login failure logging."""
        reason = "Invalid credentials"
        self.audit_logger.log_login_failure(self.test_username, reason, self.test_ip, self.test_user_agent)

        # Verify logger.warning was called (login failure uses warning level)
        mock_logger.warning.assert_called_once()
        call_args = mock_logger.warning.call_args[0][0]

        # Verify message contains expected elements
        assert "SECURITY_AUDIT: login_failure" in call_args
        assert f"User: {self.test_username}" in call_args
        assert f"IP: {self.test_ip}" in call_args
        assert "Details: {'reason': 'Invalid credentials'}" in call_args

    @patch('src.auth.security.audit_logger.logger')
    def test_log_logout(self, mock_logger):
        """Test logout logging."""
        self.audit_logger.log_logout(self.test_username, self.test_ip)

        # Verify logger.info was called
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]

        # Verify message contains expected elements
        assert "SECURITY_AUDIT: logout" in call_args
        assert f"User: {self.test_username}" in call_args
        assert f"IP: {self.test_ip}" in call_args

    @patch('src.auth.security.audit_logger.logger')
    def test_log_password_change(self, mock_logger):
        """Test password change logging."""
        self.audit_logger.log_password_change(self.test_username, self.test_ip)

        # Verify logger.info was called
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]

        # Verify message contains expected elements
        assert "SECURITY_AUDIT: password_change" in call_args
        assert f"User: {self.test_username}" in call_args
        assert f"IP: {self.test_ip}" in call_args

    @patch('src.auth.security.audit_logger.logger')
    def test_log_token_created(self, mock_logger):
        """Test token creation logging."""
        token_type = "access_token"
        self.audit_logger.log_token_created(self.test_username, token_type, self.test_ip)

        # Verify logger.info was called
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]

        # Verify message contains expected elements
        assert "SECURITY_AUDIT: token_created" in call_args
        assert f"User: {self.test_username}" in call_args
        assert f"IP: {self.test_ip}" in call_args
        assert "Details: {'token_type': 'access_token'}" in call_args

    @patch('src.auth.security.audit_logger.logger')
    def test_log_access_denied(self, mock_logger):
        """Test access denied logging."""
        resource = "/admin/users"
        reason = "Insufficient permissions"
        self.audit_logger.log_access_denied(self.test_username, resource, reason, self.test_ip)

        # Verify logger.warning was called (access denied uses warning level)
        mock_logger.warning.assert_called_once()
        call_args = mock_logger.warning.call_args[0][0]

        # Verify message contains expected elements
        assert "SECURITY_AUDIT: access_denied" in call_args
        assert f"User: {self.test_username}" in call_args
        assert f"IP: {self.test_ip}" in call_args
        assert "Details: {'resource': '/admin/users', 'reason': 'Insufficient permissions'}" in call_args

    @patch('src.auth.security.audit_logger.logger')
    def test_log_security_event_info_level(self, mock_logger):
        """Test that certain events use info level."""
        info_events = [
            SecurityEventType.LOGIN_SUCCESS,
            SecurityEventType.LOGOUT,
            SecurityEventType.PASSWORD_CHANGE,
            SecurityEventType.TOKEN_CREATED
        ]

        for event_type in info_events:
            mock_logger.reset_mock()
            self.audit_logger.log_security_event(event_type, self.test_username)
            mock_logger.info.assert_called_once()

    @patch('src.auth.security.audit_logger.logger')
    def test_log_security_event_warning_level(self, mock_logger):
        """Test that certain events use warning level."""
        warning_events = [
            SecurityEventType.LOGIN_FAILURE,
            SecurityEventType.ACCESS_DENIED
        ]

        for event_type in warning_events:
            mock_logger.reset_mock()
            details = {"reason": "test"} if event_type == SecurityEventType.LOGIN_FAILURE else {"resource": "test", "reason": "test"}
            self.audit_logger.log_security_event(event_type, self.test_username, details)
            mock_logger.warning.assert_called_once()

    @patch('src.auth.security.audit_logger.logger')
    def test_log_security_event_default_info_level(self, mock_logger):
        """Test that unknown events default to info level."""
        # Test with a custom event type that's not in the predefined lists
        self.audit_logger.log_security_event(SecurityEventType.TOKEN_REVOKED, self.test_username)
        mock_logger.info.assert_called_once()

    def test_security_event_type_values(self):
        """Test that SecurityEventType enum has expected values."""
        assert SecurityEventType.LOGIN_SUCCESS.value == "login_success"
        assert SecurityEventType.LOGIN_FAILURE.value == "login_failure"
        assert SecurityEventType.LOGOUT.value == "logout"
        assert SecurityEventType.PASSWORD_CHANGE.value == "password_change"
        assert SecurityEventType.TOKEN_CREATED.value == "token_created"
        assert SecurityEventType.TOKEN_REVOKED.value == "token_revoked"
        assert SecurityEventType.ACCESS_DENIED.value == "access_denied"