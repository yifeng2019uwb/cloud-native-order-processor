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
from ...shared.logging import BaseLogger, LogActions, Loggers
from typing import Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

from ...exceptions.shared_exceptions import CNOPTokenExpiredException, CNOPTokenInvalidException
from ...data.entities.user import DEFAULT_USER_ROLE

# Create logger instance for token management
logger = BaseLogger(Loggers.AUDIT, log_to_file=True)


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
            CNOPTokenInvalidException: If token creation failed
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
            logger.info(
                action=LogActions.SECURITY_EVENT,
                message=f"Access token created for user {username} with role {role}",
                user=username,
                extra={"role": role, "expires_in_hours": self.jwt_expiration_hours}
            )

            return {
                "access_token": token,
                "token_type": "bearer",
                "expires_in": self.jwt_expiration_hours * 3600,  # Convert hours to seconds
                "expires_at": expire.isoformat()
            }
        except Exception as e:
            logger.error(
                action=LogActions.ERROR,
                message=f"Error creating access token for user {username}",
                user=username,
                extra={"error": str(e), "error_type": type(e).__name__}
            )
            raise CNOPTokenInvalidException("Token creation failed")

    def verify_access_token(self, token: str) -> Optional[str]:
        """
        Verify and decode JWT access token.

        Args:
            token: JWT token string

        Returns:
            Username if token is valid, None otherwise

        Raises:
            CNOPTokenExpiredException: If token is expired
            CNOPTokenInvalidException: If token is invalid
        """
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])

            # Check token type
            if payload.get("type") != "access_token":
                logger.warning(
                    action=LogActions.ERROR,
                    message="Invalid token type",
                    extra={"token_type": payload.get("type")}
                )
                raise CNOPTokenInvalidException("Invalid token type")

            # Extract username
            username: str = payload.get("sub")
            if username is None:
                logger.warning(
                    action=LogActions.ERROR,
                    message="Token missing subject (username)"
                )
                raise CNOPTokenInvalidException("Token missing subject")

            logger.debug(
                action=LogActions.SECURITY_EVENT,
                message=f"Token verified for user: {username}",
                user=username
            )
            return username

        except jwt.ExpiredSignatureError:
            logger.warning(
                action=LogActions.ERROR,
                message="Token has expired"
            )
            raise CNOPTokenExpiredException("Token has expired")
        except JWTError:
            logger.warning(
                action=LogActions.ERROR,
                message="Invalid token provided"
            )
            raise CNOPTokenInvalidException("Invalid token")
        except CNOPTokenInvalidException:
            # Re-raise CNOPTokenInvalidException without wrapping
            raise
        except Exception as e:
            logger.error(
                action=LogActions.ERROR,
                message=f"Unexpected error verifying token: {e}",
                extra={"error": str(e), "error_type": type(e).__name__}
            )
            raise CNOPTokenInvalidException("Token verification failed")

    def validate_token_comprehensive(self, token: str) -> Dict[str, Any]:
        """
        Validate JWT token and extract comprehensive user context.

        Args:
            token: JWT token string

        Returns:
            Dictionary with comprehensive user context including username, role, expiration, etc.

        Raises:
            CNOPTokenExpiredException: If token is expired
            CNOPTokenInvalidException: If token is invalid
        """
        try:
            logger.info(
                action=LogActions.LogActions.SECURITY_EVENT,
                message="Starting comprehensive token validation"
            )

            # Parse and validate token
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])

            # Check token type
            if payload.get("type") != "access_token":
                logger.warning(
                    action=LogActions.ERROR,
                    message="Invalid token type: %s (expected: access_token)",
                    extra={"token_type": payload.get("type")}
                )
                raise CNOPTokenInvalidException("Invalid token type")

            # Extract username
            username: str = payload.get("sub")
            if username is None:
                logger.warning(
                    action=LogActions.ERROR,
                    message="Token missing subject (username)"
                )
                raise CNOPTokenInvalidException("Token missing subject")

            # Check if token is expired
            exp_timestamp = payload.get("exp")
            if exp_timestamp is None:
                logger.warning(
                    action=LogActions.ERROR,
                    message="Token missing expiration timestamp"
                )
                raise CNOPTokenInvalidException("Token missing expiration timestamp")

            # Check if token is expired
            if self.is_token_expired(token):
                logger.warning(
                    action=LogActions.ERROR,
                    message="Token has expired"
                )
                raise CNOPTokenExpiredException("Token has expired")

            # Extract additional context
            context = {
                "username": username,
                "exp": exp_timestamp,
                "iat": payload.get("iat"),
                "iss": payload.get("iss"),
                "aud": payload.get("aud"),
                "token_type": payload.get("type")
            }

            return context

        except jwt.ExpiredSignatureError:
            logger.warning(
                action=LogActions.ERROR,
                message="Token has expired"
            )
            raise CNOPTokenExpiredException("Token has expired")
        except JWTError:
            logger.warning(
                action=LogActions.ERROR,
                message="Invalid token provided"
            )
            raise CNOPTokenInvalidException("Invalid token")
        except CNOPTokenInvalidException:
            # Re-raise CNOPTokenInvalidException without wrapping
            raise
        except Exception as e:
            logger.error(
                action=LogActions.ERROR,
                message=f"Unexpected error during comprehensive token validation: {e}",
                extra={"error": str(e), "error_type": type(e).__name__}
            )
            raise CNOPTokenInvalidException("Token validation failed")

    def decode_token_payload(self, token: str) -> Dict[str, Any]:
        """
        Decode token payload without verification.

        Args:
            token: Token to decode

        Returns:
            Token payload as dictionary

        Raises:
            CNOPTokenInvalidException: If token is malformed
        """
        try:
            # Decode without verification (for debugging only)
            payload = jwt.decode(token, self.jwt_secret, options={"verify_signature": False}, algorithms=[self.jwt_algorithm])
            return payload
        except Exception as e:
            logger.error(
                action=LogActions.ERROR,
                message=f"Error decoding token payload: {e}",
                extra={"error": str(e), "error_type": type(e).__name__}
            )
            raise CNOPTokenInvalidException("Token decode failed")

    def is_token_expired(self, token: str) -> bool:
        """
        Check if a token is expired.

        Args:
            token: JWT token string

        Returns:
            bool: True if token is expired, False otherwise
        """
        try:
            # Decode without verification to check expiration
            payload = jwt.decode(token, self.jwt_secret, options={"verify_signature": False}, algorithms=[self.jwt_algorithm])
            exp_timestamp = payload.get("exp")

            if exp_timestamp is None:
                logger.warning(
                    action=LogActions.ERROR,
                    message="Token missing expiration timestamp"
                )
                return True

            # Check if current time is past expiration
            current_time = datetime.now(timezone.utc).timestamp()
            return current_time > exp_timestamp

        except Exception as e:
            logger.warning(
                action=LogActions.ERROR,
                message=f"Error checking token expiration: {e}"
            )
            return True

    def refresh_token(self, token: str) -> str:
        """
        Refresh an expired token.

        Args:
            token: JWT token string

        Returns:
            str: New JWT token

        Raises:
            CNOPTokenInvalidException: If token cannot be refreshed
        """
        try:
            # Decode the old token to extract user info
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            username = payload.get("sub")

            if not username:
                logger.error(
                    action=LogActions.ERROR,
                    message="Cannot refresh token: missing username"
                )
                raise CNOPTokenInvalidException("Cannot refresh token: missing username")

            # Create new token with extended expiration
            return self.create_access_token(username)

        except Exception as e:
            logger.error(
                action=LogActions.ERROR,
                message=f"Failed to refresh token: {e}"
            )
            raise CNOPTokenInvalidException("Failed to refresh token")