"""
Basic unit tests for BaseLogger class.

Simple tests to verify the logging functionality works.
"""

# Standard library imports
import json
from unittest.mock import patch

# Third-party imports
import pytest

# Local imports
from src.shared.logging.base_logger import BaseLogger, create_logger


class TestBaseLogger:
    """Basic test cases for BaseLogger class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.service_name = "test_service"
        self.logger = BaseLogger(self.service_name)

    def test_init_basic(self):
        """Test basic logger initialization."""
        assert self.logger.service_name == self.service_name
        assert self.logger.log_to_file is False

    def test_generate_request_id(self):
        """Test request ID generation."""
        request_id = self.logger._generate_request_id()
        assert request_id.startswith("req-")
        assert len(request_id) == 12  # "req-" + 8 hex chars

    def test_format_timestamp(self):
        """Test timestamp formatting."""
        timestamp = self.logger._format_timestamp()
        assert timestamp.endswith("Z")
        assert "T" in timestamp

    def test_log_basic(self):
        """Test basic logging functionality."""
        with patch('sys.stdout.write') as mock_stdout:
            self.logger.log("INFO", "test_action", "Test message")

            # Verify stdout.write was called
            mock_stdout.assert_called_once()

            # Parse the logged JSON
            logged_data = json.loads(mock_stdout.call_args[0][0])

            # Verify required fields
            assert logged_data["level"] == "INFO"
            assert logged_data["action"] == "test_action"
            assert logged_data["message"] == "Test message"
            assert logged_data["service"] == self.service_name
            assert "timestamp" in logged_data
            assert "request_id" in logged_data

    def test_log_with_optional_fields(self):
        """Test logging with optional fields."""
        with patch('sys.stdout.write') as mock_stdout:
            self.logger.log(
                "INFO", "test_action", "Test message",
                user="test_user",
                duration_ms=150,
                extra={"key": "value"},
                request_id="custom-req-123"
            )

            logged_data = json.loads(mock_stdout.call_args[0][0])

            # Verify optional fields
            assert logged_data["user"] == "test_user"
            assert logged_data["duration_ms"] == 150
            assert logged_data["extra"]["key"] == "value"
            assert logged_data["request_id"] == "custom-req-123"

    def test_log_levels(self):
        """Test that all log levels work correctly."""
        with patch('sys.stdout.write') as mock_stdout:
            # Test info level
            self.logger.info("test_info", "Info message")
            mock_stdout.assert_called()

            # Test warning level
            self.logger.warning("test_warning", "Warning message")
            mock_stdout.assert_called()

            # Test error level
            self.logger.error("test_error", "Error message")
            mock_stdout.assert_called()

    def test_create_logger_function(self):
        """Test the convenience create_logger function."""
        logger = create_logger("test_service")
        assert isinstance(logger, BaseLogger)
        assert logger.service_name == "test_service"

    def test_json_encoding(self):
        """Test JSON encoding handles special characters correctly."""
        with patch('sys.stdout.write') as mock_stdout:
            # Test with special characters
            special_message = "Test message with émojis 🚀 and unicode"
            self.logger.info("test_action", special_message)

            # Verify JSON was created correctly
            logged_data = json.loads(mock_stdout.call_args[0][0])
            assert logged_data["message"] == special_message

    def test_request_id_uniqueness(self):
        """Test that request IDs are unique across multiple logs."""
        with patch('sys.stdout.write') as mock_stdout:
            # Log multiple messages
            for i in range(3):
                self.logger.info("test_action", f"Message {i}")

            # Extract request IDs
            calls = [json.loads(call[0][0]) for call in mock_stdout.call_args_list]
            request_ids = [call["request_id"] for call in calls]

            # Verify all request IDs are unique
            assert len(set(request_ids)) == 3
            assert len(request_ids) == 3
