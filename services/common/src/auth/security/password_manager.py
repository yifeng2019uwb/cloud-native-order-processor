"""
Password Manager for secure password operations.

This module provides centralized password hashing, validation, and management
using industry-standard cryptographic algorithms.

Responsibilities:
- Password hashing (bcrypt)
- Password verification
- Password strength validation
"""

import re
from typing import Optional

import bcrypt

from ...exceptions import CNOPEntityValidationException
from ...shared.logging import BaseLogger, LoggerName

logger = BaseLogger(LoggerName.AUDIT, log_to_file=True)
ENCODE_UTF_8 = 'utf-8'


class PasswordManager:
    """
    Centralized password management for secure password operations.

    Provides password hashing, verification, and strength validation
    using industry-standard cryptographic algorithms.
    """

    def __init__(self):
        """Initialize the password manager."""
        pass

    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.

        Args:
            password: Plain text password to hash

        Returns:
            Hashed password string

        Raises:
            CNOPEntityValidationException: If password is empty or invalid
        """
        if not password or not isinstance(password, str):
            raise CNOPEntityValidationException("Password must be a non-empty string")

        # Generate salt and hash password using bcrypt
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(ENCODE_UTF_8), salt)
        return hashed.decode(ENCODE_UTF_8)

    def verify_password(self, password: str, hashed: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            password: Plain text password to verify
            hashed: Hashed password to compare against

        Returns:
            True if password matches hash, False otherwise

        Raises:
            CNOPEntityValidationException: If inputs are invalid
        """
        if not password or not isinstance(password, str):
            raise CNOPEntityValidationException("Password must be a non-empty string")

        if not hashed or not isinstance(hashed, str):
            raise CNOPEntityValidationException("Hash must be a non-empty string")

        # Verify password using bcrypt
        return bcrypt.checkpw(password.encode(ENCODE_UTF_8), hashed.encode(ENCODE_UTF_8))
