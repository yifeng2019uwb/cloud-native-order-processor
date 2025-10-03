"""
Unit tests for header validator

Tests the HeaderValidator class for gateway authentication.
"""

import os
import sys
from typing import Dict, Optional

import pytest
from fastapi import HTTPException, status

# Add the common module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

# Import the actual HeaderValidator from source files
from src.auth.gateway.header_validator import HeaderValidator


class TestHeaderValidator:
    """Test HeaderValidator class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.validator = HeaderValidator()

    def test_initialization(self):
        """Test HeaderValidator initialization"""
        assert hasattr(self.validator, 'required_headers')
        assert isinstance(self.validator.required_headers, list)
        assert len(self.validator.required_headers) == 4
        assert 'X-User-ID' in self.validator.required_headers
        assert 'X-User-Role' in self.validator.required_headers
        assert 'X-Request-ID' in self.validator.required_headers
        assert 'X-Source-Service' in self.validator.required_headers

    def test_validate_gateway_headers_success(self):
        """Test successful header validation"""
        headers = {
            'X-User-ID': 'user123',
            'X-User-Role': 'customer',
            'X-Request-ID': 'req-456',
            'X-Source-Service': 'gateway'
        }

        result = self.validator.validate_gateway_headers(headers)
        assert result is True

    def test_validate_gateway_headers_missing_single_header(self):
        """Test header validation with one missing header"""
        headers = {
            'X-User-ID': 'user123',
            'X-User-Role': 'customer',
            'X-Request-ID': 'req-456'
            # Missing X-Source-Service
        }

        with pytest.raises(HTTPException) as exc_info:
            self.validator.validate_gateway_headers(headers)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Missing required gateway headers" in str(exc_info.value.detail)
        assert "X-Source-Service" in str(exc_info.value.detail)

    def test_validate_gateway_headers_missing_multiple_headers(self):
        """Test header validation with multiple missing headers"""
        headers = {
            'X-User-ID': 'user123'
            # Missing X-User-Role, X-Request-ID, X-Source-Service
        }

        with pytest.raises(HTTPException) as exc_info:
            self.validator.validate_gateway_headers(headers)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Missing required gateway headers" in str(exc_info.value.detail)
        assert "X-User-Role" in str(exc_info.value.detail)
        assert "X-Request-ID" in str(exc_info.value.detail)
        assert "X-Source-Service" in str(exc_info.value.detail)

    def test_validate_gateway_headers_empty_headers(self):
        """Test header validation with empty headers"""
        headers = {}

        with pytest.raises(HTTPException) as exc_info:
            self.validator.validate_gateway_headers(headers)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Missing required gateway headers" in str(exc_info.value.detail)

    def test_extract_user_from_headers_success(self):
        """Test successful user extraction from headers"""
        headers = {
            'X-User-ID': 'user123',
            'X-User-Role': 'customer',
            'X-Request-ID': 'req-456',
            'X-Source-Service': 'gateway'
        }

        result = self.validator.extract_user_from_headers(headers)

        assert isinstance(result, dict)
        assert result['user_id'] == 'user123'
        assert result['user_role'] == 'customer'
        assert result['request_id'] == 'req-456'
        assert result['source_service'] == 'gateway'

    def test_extract_user_from_headers_missing_headers(self):
        """Test user extraction with missing headers"""
        headers = {
            'X-User-ID': 'user123'
            # Missing other required headers
        }

        with pytest.raises(HTTPException) as exc_info:
            self.validator.extract_user_from_headers(headers)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST

    def test_is_authenticated_success(self):
        """Test authentication check with valid headers"""
        headers = {
            'X-User-ID': 'user123',
            'X-User-Role': 'customer',
            'X-Request-ID': 'req-456',
            'X-Source-Service': 'gateway'
        }

        result = self.validator.is_authenticated(headers)
        assert result is True

    def test_is_authenticated_failure(self):
        """Test authentication check with invalid headers"""
        headers = {
            'X-User-ID': 'user123'
            # Missing other required headers
        }

        result = self.validator.is_authenticated(headers)
        assert result is False

    def test_is_authenticated_empty_headers(self):
        """Test authentication check with empty headers"""
        headers = {}

        result = self.validator.is_authenticated(headers)
        assert result is False

    def test_get_user_role_success(self):
        """Test getting user role from headers"""
        headers = {
            'X-User-ID': 'user123',
            'X-User-Role': 'admin',
            'X-Request-ID': 'req-456',
            'X-Source-Service': 'gateway'
        }

        result = self.validator.get_user_role(headers)
        assert result == 'admin'

    def test_get_user_role_missing(self):
        """Test getting user role when not present"""
        headers = {
            'X-User-ID': 'user123',
            'X-Request-ID': 'req-456',
            'X-Source-Service': 'gateway'
            # Missing X-User-Role
        }

        result = self.validator.get_user_role(headers)
        assert result is None

    def test_get_user_id_success(self):
        """Test getting user ID from headers"""
        headers = {
            'X-User-ID': 'user123',
            'X-User-Role': 'customer',
            'X-Request-ID': 'req-456',
            'X-Source-Service': 'gateway'
        }

        result = self.validator.get_user_id(headers)
        assert result == 'user123'

    def test_get_user_id_missing(self):
        """Test getting user ID when not present"""
        headers = {
            'X-User-Role': 'customer',
            'X-Request-ID': 'req-456',
            'X-Source-Service': 'gateway'
            # Missing X-User-ID
        }

        result = self.validator.get_user_id(headers)
        assert result is None

    def test_get_user_role_empty_headers(self):
        """Test getting user role with empty headers"""
        headers = {}

        result = self.validator.get_user_role(headers)
        assert result is None

    def test_get_user_id_empty_headers(self):
        """Test getting user ID with empty headers"""
        headers = {}

        result = self.validator.get_user_id(headers)
        assert result is None
