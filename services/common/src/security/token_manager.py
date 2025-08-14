"""
Token Manager for JWT and session token operations.

This module provides centralized token generation, validation, and management
for JWT tokens, refresh tokens, and API keys.

Responsibilities:
- JWT token generation and validation
- Refresh token management
- API key generation and validation
- Token blacklisting and revocation
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

from ..exceptions.shared_exceptions import TokenExpiredException, TokenInvalidException
from ..entities.user import DEFAULT_USER_ROLE

logger = logging.getLogger(__name__)


class TokenManager:
    """
    Centralized token management for JWT and session operations.

    Provides token generation, validation, and management for various
    authentication and authorization scenarios.
    """

    def __init__(self):
        """Initialize the token manager."""
        # JWT Configuration
        self.jwt_secret = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
        self.jwt_algorithm = "HS256"
        self.jwt_expiration_hours = 1

    def create_access_token(self, username: str, role: str = DEFAULT_USER_ROLE, expires_delta: Optional[timedelta] = None) -> Dict[str, Any]:
        """
        Create JWT access token for authenticated user.

        Args:
            username: User's username
            role: User's role (default: "customer" from enum)
            expires_delta: Optional custom expiration time

        Returns:
            Dict with token information including access_token, token_type, expires_in

        Raises:
            TokenInvalidException: If token creation fails
        """
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(hours=self.jwt_expiration_hours)

        payload = {
            "sub": username,
            "role": role,  # Include role in JWT payload
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access_token"
        }

        try:
            token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
            logger.info(f"Access token created for user: {username} with role: {role}")

            return {
                "access_token": token,
                "token_type": "bearer",
                "expires_in": self.jwt_expiration_hours * 3600,  # Convert hours to seconds
                "expires_at": expire.isoformat()
            }
        except Exception as e:
            logger.error(f"Error creating access token: {username}")
            raise TokenInvalidException("Token creation failed")

    def verify_access_token(self, token: str) -> Optional[str]:
        """
        Verify and decode JWT access token.

        Args:
            token: JWT token string

        Returns:
            Username if token is valid, None otherwise

        Raises:
            TokenExpiredException: If token is expired
            TokenInvalidException: If token is invalid
        """
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])

            # Check token type
            if payload.get("type") != "access_token":
                logger.warning("Invalid token type")
                raise TokenInvalidException("Invalid token type")

            # Extract username
            username: str = payload.get("sub")
            if username is None:
                logger.warning("Token missing subject (username)")
                raise TokenInvalidException("Token missing subject")

            logger.debug(f"Token verified for user: {username}")
            return username

        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            raise TokenExpiredException("Token has expired")
        except JWTError:
            logger.warning("Invalid token provided")
            raise TokenInvalidException("Invalid token")
        except TokenInvalidException:
            # Re-raise TokenInvalidException without wrapping
            raise
        except Exception as e:
            logger.error(f"Unexpected error verifying token: {e}")
            raise TokenInvalidException("Token verification failed")

    def decode_token_payload(self, token: str) -> Dict[str, Any]:
        """
        Decode token payload without verification.

        Args:
            token: Token to decode

        Returns:
            Token payload as dictionary

        Raises:
            TokenInvalidException: If token is malformed
        """
        try:
            # Decode without verification (for debugging only)
            payload = jwt.decode(token, self.jwt_secret, options={"verify_signature": False}, algorithms=[self.jwt_algorithm])
            return payload
        except Exception as e:
            logger.error(f"Error decoding token payload: {e}")
            raise TokenInvalidException("Token decode failed")

    def is_token_expired(self, token: str) -> bool:
        """
        Check if token is expired without verification.

        Args:
            token: Token to check

        Returns:
            True if token is expired, False otherwise
        """
        try:
            payload = self.decode_token_payload(token)
            exp_timestamp = payload.get("exp")

            if exp_timestamp is None:
                return True

            current_timestamp = datetime.now(timezone.utc).timestamp()
            return current_timestamp > exp_timestamp

        except Exception as e:
            logger.error(f"Error checking token expiration: {e}")
            return True