"""
Unit tests for PasswordManager class.
"""
import pytest
from unittest.mock import patch, MagicMock
from src.security.password_manager import PasswordManager
from src.exceptions.shared_exceptions import EntityValidationException


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
        with pytest.raises(EntityValidationException, match="Password must be a non-empty string"):
            self.password_manager.hash_password("")

    def test_hash_password_none(self):
        """Test password hashing with None."""
        with pytest.raises(EntityValidationException, match="Password must be a non-empty string"):
            self.password_manager.hash_password(None)

    def test_hash_password_non_string(self):
        """Test password hashing with non-string input."""
        with pytest.raises(EntityValidationException, match="Password must be a non-empty string"):
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

        with pytest.raises(EntityValidationException, match="Password must be a non-empty string"):
            self.password_manager.verify_password("", hashed)

    def test_verify_password_empty_hash(self):
        """Test password verification with empty hash."""
        with pytest.raises(EntityValidationException, match="Hash must be a non-empty string"):
            self.password_manager.verify_password("testpassword123", "")

    def test_verify_password_none_hash(self):
        """Test password verification with None hash."""
        with pytest.raises(EntityValidationException, match="Hash must be a non-empty string"):
            self.password_manager.verify_password("testpassword123", None)

    def test_validate_password_strength_success(self):
        """Test successful password strength validation."""
        password = "TestPassword123!"
        assert self.password_manager.validate_password_strength(password) is True

    def test_validate_password_strength_too_short(self):
        """Test password strength validation with too short password."""
        with pytest.raises(EntityValidationException, match="Password must be at least 8 characters long"):
            self.password_manager.validate_password_strength("short")

    def test_validate_password_strength_exactly_8_chars(self):
        """Test password strength validation with exactly 8 characters."""
        password = "Test123!"
        assert self.password_manager.validate_password_strength(password) is True

    def test_validate_password_strength_very_long(self):
        """Test password strength validation with very long password."""
        password = "A" * 129  # 129 characters
        with pytest.raises(EntityValidationException, match="Password must be no more than 128 characters long"):
            self.password_manager.validate_password_strength(password)

    def test_validate_password_strength_empty_string(self):
        """Test password strength validation with empty string."""
        with pytest.raises(EntityValidationException, match="Password must be a non-empty string"):
            self.password_manager.validate_password_strength("")

    def test_validate_password_strength_none(self):
        """Test password strength validation with None."""
        with pytest.raises(EntityValidationException, match="Password must be a non-empty string"):
            self.password_manager.validate_password_strength(None)

    def test_validate_password_strength_non_string(self):
        """Test password strength validation with non-string input."""
        with pytest.raises(EntityValidationException, match="Password must be a non-empty string"):
            self.password_manager.validate_password_strength(123)

    def test_integration_hash_verify_validate(self):
        """Test integration of hash, verify, and validate methods."""
        password = "TestPassword123!"

        # Validate password strength
        assert self.password_manager.validate_password_strength(password) is True

        # Hash password
        hashed = self.password_manager.hash_password(password)
        assert hashed != password

        # Verify password
        assert self.password_manager.verify_password(password, hashed) is True
        assert self.password_manager.verify_password("wrongpassword", hashed) is False