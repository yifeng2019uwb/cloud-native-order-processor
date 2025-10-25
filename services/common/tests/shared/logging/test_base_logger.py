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
from src.shared.logging.base_logger import BaseLogger, create_logger, LogEntry
from tests.utils.dependency_constants import LOGGER_WRITE_TO_FILE

# =============================================================================
# LOCAL TEST VARIABLES - Avoid hardcoded values in tests
# =============================================================================

# Basic test data
TEST_SERVICE_NAME = "test_service"
TEST_MESSAGE = "Test message"
TEST_USER = "test_user"
TEST_REQUEST_ID = "req-test123"

# Log levels
TEST_LOG_LEVEL_INFO = "INFO"
TEST_LOG_LEVEL_WARN = "WARN"
TEST_LOG_LEVEL_ERROR = "ERROR"

# Log actions
TEST_ACTION = "TEST_ACTION"
TEST_INFO_ACTION = "TEST_INFO_ACTION"

# Log messages
TEST_INFO_MESSAGE = "Test info message"
TEST_SPECIAL_MESSAGE = "Test message with special chars: @#$%^&*()"
TEST_EXTRA_DATA = "Test extra data"

# Test counts
TEST_MESSAGE_COUNT = 5

# JSON field names
TEST_FIELD_LEVEL = "level"
TEST_FIELD_ACTION = "action"
TEST_FIELD_MESSAGE = "message"
TEST_FIELD_SERVICE = "service"
TEST_FIELD_USER = "user"
TEST_FIELD_REQUEST_ID = "request_id"
TEST_FIELD_TIMESTAMP = "timestamp"

TEST_WARNING_ACTION = "test_warning"
TEST_WARNING_MESSAGE = "Warning message"
TEST_ERROR_ACTION = "test_error"
TEST_ERROR_MESSAGE = "Error message"
TEST_SPECIAL_MESSAGE = "Test message with émojis 🚀 and unicode"
TEST_LOG_LEVEL_INFO = "INFO"


class TestBaseLogger:
    """Basic test cases for BaseLogger class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.service_name = TEST_SERVICE_NAME
        self.logger = BaseLogger(self.service_name, log_to_file=True)

    def test_init_basic(self):
        """Test basic logger initialization."""
        assert self.logger.service_name == self.service_name
        assert self.logger.log_to_file is True

    def test_generate_request_id(self):
        """Test request ID generation."""
        # Local test variables for this specific test
        expected_prefix = "req-"
        expected_length = 12

        request_id = self.logger._generate_request_id()

        # Verify using expected variables
        assert request_id.startswith(expected_prefix)
        assert len(request_id) == expected_length

    def test_format_timestamp(self):
        """Test timestamp formatting."""
        # Local test variables for this specific test
        expected_suffix = "Z"
        expected_separator = "T"

        timestamp = self.logger._format_timestamp()

        # Verify using expected variables
        assert timestamp.endswith(expected_suffix)
        assert expected_separator in timestamp

    def test_log_basic(self):
        """Test basic logging functionality."""
        with patch.object(self.logger, LOGGER_WRITE_TO_FILE) as mock_write:
            self.logger.log(TEST_LOG_LEVEL_INFO, TEST_ACTION, TEST_MESSAGE)

            # Verify file write was called
            mock_write.assert_called_once()

            # Parse the logged JSON and create LogEntry object
            logged_data = LogEntry.model_validate_json(mock_write.call_args[0][0])

            # Verify required fields
            assert logged_data.level == TEST_LOG_LEVEL_INFO
            assert logged_data.action == TEST_ACTION
            assert logged_data.message == TEST_MESSAGE
            assert logged_data.service == self.service_name
            assert logged_data.timestamp is not None
            assert logged_data.request_id is not None

    def test_log_with_optional_fields(self):
        """Test logging with optional fields."""
        with patch.object(self.logger, LOGGER_WRITE_TO_FILE) as mock_write:
            self.logger.log(
                TEST_LOG_LEVEL_INFO, TEST_ACTION, TEST_MESSAGE,
                user=TEST_USER,
                extra=TEST_EXTRA_DATA,
                request_id=TEST_FIELD_REQUEST_ID
            )

            logged_data = LogEntry.model_validate_json(mock_write.call_args[0][0])

            # Verify optional fields
            assert logged_data.user == TEST_USER
            assert logged_data.extra == TEST_EXTRA_DATA
            assert logged_data.request_id == TEST_FIELD_REQUEST_ID

    def test_log_levels(self):
        """Test that all log levels work correctly."""
        with patch.object(self.logger, LOGGER_WRITE_TO_FILE) as mock_write:
            # Test info level
            self.logger.info(TEST_INFO_ACTION, TEST_INFO_MESSAGE)
            mock_write.assert_called()

            # Test warning level
            self.logger.warning(TEST_WARNING_ACTION, TEST_WARNING_MESSAGE)
            mock_write.assert_called()

            # Test error level
            self.logger.error(TEST_ERROR_ACTION, TEST_ERROR_MESSAGE)
            mock_write.assert_called()

    def test_create_logger_function(self):
        """Test the convenience create_logger function."""
        logger = create_logger(TEST_SERVICE_NAME)
        assert isinstance(logger, BaseLogger)
        assert logger.service_name == TEST_SERVICE_NAME

    def test_json_encoding(self):
        """Test JSON encoding handles special characters correctly."""
        with patch.object(self.logger, LOGGER_WRITE_TO_FILE) as mock_write:
            # Test with special characters
            self.logger.info(TEST_ACTION, TEST_SPECIAL_MESSAGE)

            # Verify JSON was created correctly
            logged_data = LogEntry.model_validate_json(mock_write.call_args[0][0])
            assert logged_data.message == TEST_SPECIAL_MESSAGE

    def test_request_id_uniqueness(self):
        """Test that request IDs are unique across multiple logs."""
        with patch.object(self.logger, LOGGER_WRITE_TO_FILE) as mock_write:
            # Log multiple messages
            for i in range(TEST_MESSAGE_COUNT):
                self.logger.info(TEST_ACTION, f"Message {i}")

            # Extract request IDs
            calls = [LogEntry.model_validate_json(call[0][0]) for call in mock_write.call_args_list]
            request_ids = [call.request_id for call in calls]

            # Verify all request IDs are unique
            assert len(set(request_ids)) == TEST_MESSAGE_COUNT
            assert len(request_ids) == TEST_MESSAGE_COUNT
