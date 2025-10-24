"""
Unit tests for request utilities

Tests the get_request_id_from_request function for request ID extraction.
"""

import os
import sys
from unittest.mock import Mock

import pytest

# Add the common module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

# Import the actual function and constants from source files
from src.auth.gateway.header_validator import get_request_id_from_request
from src.shared.constants.api_constants import RequestHeaders, RequestHeaderDefaults


class TestRequestUtilities:
    """Test request utility functions"""

    # Test constants
    TEST_REQUEST_ID = "req-12345"
    TEST_REQUEST_ID_2 = "req-67890"
    TEST_AUTH_TOKEN = "Bearer token123"
    TEST_CONTENT_TYPE = "application/json"
    TEST_USER_AGENT = "test-agent"
    EMPTY_STRING = ""

    def test_get_request_id_from_request_with_header(self):
        """Test request ID extraction when header is present"""
        # Mock request with X-Request-ID header
        mock_request = Mock()
        mock_request.headers = {RequestHeaders.REQUEST_ID: self.TEST_REQUEST_ID}

        result = get_request_id_from_request(mock_request)

        assert result == self.TEST_REQUEST_ID

    def test_get_request_id_from_request_without_header(self):
        """Test request ID extraction when header is missing"""
        # Mock request without X-Request-ID header
        mock_request = Mock()
        mock_request.headers = {}

        result = get_request_id_from_request(mock_request)

        assert result == RequestHeaderDefaults.REQUEST_ID_DEFAULT

    def test_get_request_id_from_request_with_none_header(self):
        """Test request ID extraction when header is None"""
        # Mock request with None header value
        mock_request = Mock()
        mock_request.headers = {RequestHeaders.REQUEST_ID: None}

        result = get_request_id_from_request(mock_request)

        assert result == RequestHeaderDefaults.REQUEST_ID_DEFAULT

    def test_get_request_id_from_request_with_empty_header(self):
        """Test request ID extraction when header is empty string"""
        # Mock request with empty string header value
        mock_request = Mock()
        mock_request.headers = {RequestHeaders.REQUEST_ID: self.EMPTY_STRING}

        result = get_request_id_from_request(mock_request)

        assert result == RequestHeaderDefaults.REQUEST_ID_DEFAULT

    def test_get_request_id_from_request_with_other_headers(self):
        """Test request ID extraction with other headers present but not X-Request-ID"""
        # Mock request with other headers but no X-Request-ID
        mock_request = Mock()
        mock_request.headers = {
            RequestHeaders.AUTHORIZATION: self.TEST_AUTH_TOKEN,
            RequestHeaders.CONTENT_TYPE: self.TEST_CONTENT_TYPE,
            RequestHeaders.USER_AGENT: self.TEST_USER_AGENT
        }

        result = get_request_id_from_request(mock_request)

        assert result == RequestHeaderDefaults.REQUEST_ID_DEFAULT

    def test_get_request_id_from_request_with_multiple_headers(self):
        """Test request ID extraction with multiple headers including X-Request-ID"""
        # Mock request with multiple headers including X-Request-ID
        mock_request = Mock()
        mock_request.headers = {
            RequestHeaders.AUTHORIZATION: self.TEST_AUTH_TOKEN,
            RequestHeaders.REQUEST_ID: self.TEST_REQUEST_ID_2,
            RequestHeaders.CONTENT_TYPE: self.TEST_CONTENT_TYPE,
            RequestHeaders.USER_AGENT: self.TEST_USER_AGENT
        }

        result = get_request_id_from_request(mock_request)

        assert result == self.TEST_REQUEST_ID_2
