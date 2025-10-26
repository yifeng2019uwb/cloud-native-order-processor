"""
Unit tests for PasswordManager class.
"""
# Standard library imports
from unittest.mock import MagicMock, patch

# Third-party imports
import pytest

# Local imports
from src.auth.security.password_manager import PasswordManager
from src.exceptions import CNOPEntityValidationException


class TestPasswordManager:
    """Test cases for PasswordManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.password_manager = PasswordManager()

    def test_hash_password_success(self):
        """Test successful password hashing."""
        password = "testpassword123"
        hashed = self.password_manager.hash_password(password)

        # Verify hash is different from original password
        assert hashed != password
        # Verify hash is a string
        assert isinstance(hashed, str)
        # Verify hash is not empty
        assert len(hashed) > 0

    def test_hash_password_empty_string(self):
        """Test password hashing with empty string."""
        with pytest.raises(CNOPEntityValidationException, match="Password must be a non-empty string"):
            self.password_manager.hash_password("")

    def test_hash_password_none(self):
        """Test password hashing with None."""
        with pytest.raises(CNOPEntityValidationException, match="Password must be a non-empty string"):
            self.password_manager.hash_password(None)

    def test_hash_password_non_string(self):
        """Test password hashing with non-string input."""
        with pytest.raises(CNOPEntityValidationException, match="Password must be a non-empty string"):
            self.password_manager.hash_password(123)

    def test_verify_password_success(self):
        """Test successful password verification."""
        password = "testpassword123"
        hashed = self.password_manager.hash_password(password)

        # Verify the password matches the hash
        assert self.password_manager.verify_password(password, hashed) is True

    def test_verify_password_wrong_password(self):
        """Test password verification with wrong password."""
        password = "testpassword123"
        hashed = self.password_manager.hash_password(password)

        # Verify wrong password doesn't match
        assert self.password_manager.verify_password("wrongpassword", hashed) is False

    def test_verify_password_empty_password(self):
        """Test password verification with empty password."""
        hashed = self.password_manager.hash_password("testpassword123")

        with pytest.raises(CNOPEntityValidationException, match="Password must be a non-empty string"):
            self.password_manager.verify_password("", hashed)

    def test_verify_password_empty_hash(self):
        """Test password verification with empty hash."""
        with pytest.raises(CNOPEntityValidationException, match="Hash must be a non-empty string"):
            self.password_manager.verify_password("testpassword123", "")

    def test_verify_password_none_hash(self):
        """Test password verification with None hash."""
        with pytest.raises(CNOPEntityValidationException, match="Hash must be a non-empty string"):
            self.password_manager.verify_password("testpassword123", None)


    def test_integration_hash_verify_validate(self):
        """Test integration of hash, verify, and validate methods."""
        password = "TestPassword123!"

        # Hash password
        hashed = self.password_manager.hash_password(password)
        assert hashed != password

        # Verify password
        assert self.password_manager.verify_password(password, hashed) is True
        assert self.password_manager.verify_password("wrongpassword", hashed) is False