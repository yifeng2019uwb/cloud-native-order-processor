"""
JWT Validator Service for Auth Service.

This service handles JWT token validation and user context extraction.
Copied from common package to ensure independence.
"""

import os
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from jose import jwt, JWTError

from exceptions.auth_exceptions import TokenExpiredException, TokenInvalidException

logger = logging.getLogger(__name__)


class JWTValidator:
    """
    JWT token validation service for Auth Service.

    Provides token validation, user context extraction, and token metadata.
    """

    def __init__(self):
        """Initialize the JWT validator."""
        # JWT Configuration
        self.jwt_secret = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
        self.jwt_algorithm = "HS256"

        logger.info("JWT Validator initialized - algorithm: %s, secret_configured: %s",
                   self.jwt_algorithm,
                   bool(self.jwt_secret != "dev-secret-key-change-in-production"))

    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate JWT token and extract user context.

        Args:
            token: JWT token string

        Returns:
            Dictionary with validation result and user context

        Raises:
            TokenExpiredException: If token is expired
            TokenInvalidException: If token is invalid
        """
        try:
            logger.debug("Starting token validation")

            # Parse and validate token
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])

            # Check token type
            if payload.get("type") != "access_token":
                logger.warning("Invalid token type: %s (expected: access_token)", payload.get("type"))
                raise TokenInvalidException("Invalid token type")

            # Extract username
            username: str = payload.get("sub")
            if username is None:
                logger.warning("Token missing subject (username)")
                raise TokenInvalidException("Token missing subject")

            # Check if token is expired
            exp_timestamp = payload.get("exp")
            if exp_timestamp is None:
                logger.warning("Token missing expiration")
                raise TokenInvalidException("Token missing expiration")

            current_timestamp = datetime.now(timezone.utc).timestamp()
            if current_timestamp > exp_timestamp:
                logger.warning("Token has expired for user: %s, expired_at: %s",
                             username,
                             datetime.fromtimestamp(exp_timestamp, tz=timezone.utc).isoformat())
                raise TokenExpiredException("Token has expired")

            # Extract additional claims
            role = payload.get("role", "customer")  # Default role
            iat_timestamp = payload.get("iat")
            issuer = payload.get("iss", "user_service")
            audience = payload.get("aud", "trading_platform")

            # Create user context
            user_context = {
                "username": username,
                "role": role,
                "is_authenticated": True,
                "expires_at": datetime.fromtimestamp(exp_timestamp, tz=timezone.utc).isoformat(),
                "created_at": datetime.fromtimestamp(iat_timestamp, tz=timezone.utc).isoformat() if iat_timestamp else None,
                "metadata": {
                    "algorithm": self.jwt_algorithm,
                    "issuer": issuer,
                    "audience": audience
                }
            }

            logger.info("Token validated successfully for user: %s, role: %s, expires_at: %s",
                       username, role, user_context["expires_at"])

            return user_context

        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired (JWT library)")
            raise TokenExpiredException("Token has expired")
        except JWTError as e:
            logger.warning("Invalid JWT token: %s", str(e))
            raise TokenInvalidException("Invalid token")
        except TokenExpiredException:
            # Re-raise TokenExpiredException without wrapping
            raise
        except TokenInvalidException:
            # Re-raise TokenInvalidException without wrapping
            raise
        except Exception as e:
            logger.error("Unexpected error verifying token: %s (type: %s)", str(e), type(e).__name__)
            raise TokenInvalidException("Token verification failed")

    def decode_token_payload(self, token: str) -> Dict[str, Any]:
        """
        Decode token payload without verification (for debugging only).

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
            logger.error("Error decoding token payload: %s", str(e))
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
            logger.error("Error checking token expiration: %s", str(e))
            return True
