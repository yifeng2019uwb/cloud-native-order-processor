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
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from pydantic import BaseModel, Field

from ...data.entities.user import DEFAULT_USER_ROLE
from ...exceptions.shared_exceptions import (CNOPTokenExpiredException,
                                             CNOPTokenInvalidException,
                                             CNOPConfigurationException)
from ...shared.logging import BaseLogger, LogAction, LoggerName, LogField, LogDefault
from .jwt_constants import JWTConfig, JwtFields, JwtResponseFields

# Create logger instance for token management
logger = BaseLogger(LoggerName.AUDIT, log_to_file=True)


class AccessTokenResponse(BaseModel):
    """Response model for access token creation"""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default=JWTConfig.TOKEN_TYPE_BEARER, description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    expires_at: str = Field(..., description="Token expiration timestamp")


class TokenContext(BaseModel):
    """Token context model for internal service use"""

    username: str = Field(..., description="Username from token subject")
    role: str = Field(..., description="User role from token")
    expiration: datetime = Field(..., description="Token expiration timestamp")
    issued_at: datetime = Field(..., description="Token issued at timestamp")
    issuer: Optional[str] = Field(None, description="Token issuer")
    audience: Optional[str] = Field(None, description="Token audience")
    token_type: str = Field(..., description="Token type")


class TokenManager:
    """
    Centralized token management for JWT and session operations.

    Provides token generation, validation, and management for various
    authentication and authorization scenarios.
    """

    def __init__(self):
        """Initialize the token manager."""
        # JWT Configuration - force required secret
        self.jwt_secret = os.getenv(JWTConfig.JWT_SECRET_KEY)
        if not self.jwt_secret:
            raise CNOPConfigurationException(
                "JWT_SECRET_KEY environment variable is required. "
                "Generate a secure secret with: openssl rand -hex 32"
            )

        # Warn if using a weak secret
        if len(self.jwt_secret) < 32:
            logger.warning(
                action=LogAction.SECURITY_EVENT,
                message="JWT_SECRET_KEY should be at least 32 characters for security"
            )

        self.jwt_algorithm = JWTConfig.ALGORITHM_HS256
        self.jwt_expiration_hours = JWTConfig.DEFAULT_EXPIRATION_HOURS

    def create_access_token(self, username: str, role: str = DEFAULT_USER_ROLE, expires_delta: Optional[timedelta] = None) -> AccessTokenResponse:
        """
        Create JWT access token for authenticated user.

        Args:
            username: User's username
            role: User's role (default: customer from enum)
            expires_delta: Optional custom expiration time

        Returns:
            AccessTokenResponse object with token information

        Raises:
            CNOPTokenInvalidException: If token creation failed
        """
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(hours=self.jwt_expiration_hours)

        payload = {
            JwtFields.SUBJECT: username,
            JwtFields.ROLE: role,
            JwtFields.EXPIRATION: expire,
            JwtFields.ISSUED_AT: datetime.now(timezone.utc),
            JwtFields.TYPE: JWTConfig.ACCESS_TOKEN_TYPE
        }

        try:
            token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
            logger.info(
                action=LogAction.SECURITY_EVENT,
                message=f"Access token created for user {username} with role {role}",
                user=username
            )

            return AccessTokenResponse(
                access_token=token,
                expires_in=self.jwt_expiration_hours * JWTConfig.SECONDS_PER_HOUR,
                expires_at=expire.isoformat()
            )
        except Exception as e:
            logger.error(
                action=LogAction.ERROR,
                message=f"Error creating access token for user {username}",
                user=username
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
            if payload.get(JwtFields.TYPE) != JWTConfig.ACCESS_TOKEN_TYPE:
                logger.warning(
                    action=LogAction.ERROR,
                    message="Invalid token type"
                )
                raise CNOPTokenInvalidException("Invalid token type")

            # Extract username
            username: str = payload.get(JwtFields.SUBJECT)
            if username is None:
                logger.warning(
                    action=LogAction.ERROR,
                    message="Token missing subject (username)"
                )
                raise CNOPTokenInvalidException("Token missing subject")

            logger.debug(
                action=LogAction.SECURITY_EVENT,
                message=f"Token verified for user: {username}",
                user=username
            )
            return username

        except jwt.ExpiredSignatureError:
            logger.warning(
                action=LogAction.ERROR,
                message="Token has expired"
            )
            raise CNOPTokenExpiredException("Token has expired")
        except JWTError:
            logger.warning(
                action=LogAction.ERROR,
                message="Invalid token provided"
            )
            raise CNOPTokenInvalidException("Invalid token")
        except CNOPTokenInvalidException:
            # Re-raise CNOPTokenInvalidException without wrapping
            raise
        except Exception as e:
            logger.error(action=LogAction.ERROR,message=f"Unexpected error verifying token: {e}")
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
                action=LogAction.SECURITY_EVENT,
                message="Starting comprehensive token validation"
            )

            # Parse and validate token
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])

            # Check token type
            if payload.get(JwtFields.TYPE) != JWTConfig.ACCESS_TOKEN_TYPE:
                logger.warning(
                    action=LogAction.ERROR,
                    message=f"Invalid token type: %s (expected: {JWTConfig.ACCESS_TOKEN_TYPE})"
                )
                raise CNOPTokenInvalidException("Invalid token type")

            # Extract username
            username: str = payload.get(JwtFields.SUBJECT)
            if username is None:
                logger.warning(
                    action=LogAction.ERROR,
                    message="Token missing subject (username)"
                )
                raise CNOPTokenInvalidException("Token missing subject")

            # Check if token is expired
            exp_timestamp = payload.get(JwtFields.EXPIRATION)
            if exp_timestamp is None:
                logger.warning(
                    action=LogAction.ERROR,
                    message="Token missing expiration timestamp"
                )
                raise CNOPTokenInvalidException("Token missing expiration timestamp")

            # Check if token is expired
            if self.is_token_expired(token):
                logger.warning(
                    action=LogAction.ERROR,
                    message="Token has expired"
                )
                raise CNOPTokenExpiredException("Token has expired")

            # Extract additional context
            context = {
                JwtFields.USERNAME: username,
                JwtFields.ROLE: payload.get(JwtFields.ROLE),
                JwtFields.EXPIRATION: exp_timestamp,
                JwtFields.ISSUED_AT: payload.get(JwtFields.ISSUED_AT),
                JwtFields.ISSUER: payload.get(JwtFields.ISSUER),
                JwtFields.AUDIENCE: payload.get(JwtFields.AUDIENCE),
                JwtFields.TYPE: payload.get(JwtFields.TYPE),
                JwtFields.METADATA: {
                    JwtFields.ROLE: payload.get(JwtFields.ROLE)
                }
            }

            return context

        except jwt.ExpiredSignatureError:
            logger.warning(
                action=LogAction.ERROR,
                message="Token has expired"
            )
            raise CNOPTokenExpiredException("Token has expired")
        except JWTError:
            logger.warning(
                action=LogAction.ERROR,
                message="Invalid token provided"
            )
            raise CNOPTokenInvalidException("Invalid token")
        except CNOPTokenInvalidException:
            # Re-raise CNOPTokenInvalidException without wrapping
            raise
        except Exception as e:
            logger.error(
                action=LogAction.ERROR,
                message=f"Unexpected error during comprehensive token validation: {e}"
            )
            raise CNOPTokenInvalidException("Token validation failed")

    # TODO: Remove if not used after testing - decode_token_payload method
    # def decode_token_payload(self, token: str) -> Dict[str, Any]:
    #     """
    #     Decode token payload without verification.

    #     Args:
    #         token: Token to decode

    #     Returns:
    #         Token payload as dictionary

    #     Raises:
    #         CNOPTokenInvalidException: If token is malformed
    #     """
    #     try:
    #         # Decode without verification (for debugging only)
    #         payload = jwt.decode(token, self.jwt_secret, options={JWTConfig.VERIFY_SIGNATURE: False}, algorithms=[self.jwt_algorithm])
    #         return payload
    #     except Exception as e:
    #         logger.error(
    #             action=LogAction.ERROR,
    #             message=f"Error decoding token payload: {e}"
    #         )
    #         raise CNOPTokenInvalidException("Token decode failed")

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
            payload = jwt.decode(token, self.jwt_secret, options={JWTConfig.VERIFY_SIGNATURE: False}, algorithms=[self.jwt_algorithm])
            exp_timestamp = payload.get(JwtFields.EXPIRATION)

            if exp_timestamp is None:
                logger.warning(
                    action=LogAction.ERROR,
                    message="Token missing expiration timestamp"
                )
                return True

            # Check if current time is past expiration
            current_time = datetime.now(timezone.utc).timestamp()
            return current_time > exp_timestamp

        except Exception as e:
            logger.warning(
                action=LogAction.ERROR,
                message=f"Error checking token expiration: {e}"
            )
            return True

    # TODO: Remove if not used after testing - refresh_token method
    # def refresh_token(self, token: str) -> str:
    #     """
    #     Refresh an expired token.

    #     Args:
    #         token: JWT token string

    #     Returns:
    #         str: New JWT token

    #     Raises:
    #         CNOPTokenInvalidException: If token cannot be refreshed
    #     """
    #     try:
    #         # Decode the old token to extract user info
    #         payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
    #         username = payload.get(JwtFields.SUBJECT)

    #         if not username:
    #             logger.error(
    #                 action=LogAction.ERROR,
    #                 message="Cannot refresh token: missing username"
    #             )
    #             raise CNOPTokenInvalidException("Cannot refresh token: missing username")

    #         # Create new token with extended expiration
    #         return self.create_access_token(username)

    #     except Exception as e:
    #         logger.error(
    #             action=LogAction.ERROR,
    #             message=f"Failed to refresh token: {e}"
    #         )
    #         raise CNOPTokenInvalidException("Failed to refresh token")
