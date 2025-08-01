"""
JWT Token utilities for user authentication
"""
import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
import logging
from common.entities.user import DEFAULT_USER_ROLE

# Import exceptions
from user_exceptions import TokenExpiredException, TokenInvalidException

logger = logging.getLogger(__name__)

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24


def create_access_token(username: str, role: str = DEFAULT_USER_ROLE, expires_delta: Optional[timedelta] = None) -> dict:
    """
    Create JWT access token for authenticated user

    Args:
        username: User's username
        role: User's role (default: "customer" from enum)
        expires_delta: Optional custom expiration time

    Returns:
        Dict with token information
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)

    payload = {
        "sub": username,
        "role": role,  # Include role in JWT payload
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access_token"
    }

    try:
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        logger.info(f"Access token created for user: {username} with role: {role}")

        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": JWT_EXPIRATION_HOURS * 3600,  # Convert hours to seconds
            "expires_at": expire.isoformat()
        }
    except Exception as e:
        logger.error(f"Error creating access token: {username}")
        raise


def verify_access_token(token: str) -> Optional[str]:
    """
    Verify and decode JWT access token

    Args:
        token: JWT token string

    Returns:
        Username if token is valid, None otherwise

    Raises:
        TokenExpiredException: If token is expired
        TokenInvalidException: If token is invalid
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

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


def decode_token_payload(token: str) -> dict:
    """
    Decode token payload without verification (for debugging)

    Args:
        token: JWT token string

    Returns:
        Token payload as dictionary
    """
    try:
        # Decode without verification (for debugging only)
        payload = jwt.decode(token, JWT_SECRET, options={"verify_signature": False}, algorithms=[JWT_ALGORITHM])
        return payload
    except Exception as e:
        logger.error(f"Error decoding token payload: {e}")
        return {}


def is_token_expired(token: str) -> bool:
    """
    Check if token is expired without verification

    Args:
        token: JWT token string

    Returns:
        True if token is expired, False otherwise
    """
    try:
        payload = decode_token_payload(token)
        exp_timestamp = payload.get("exp")

        if exp_timestamp is None:
            return True

        current_timestamp = datetime.now(timezone.utc).timestamp()
        return current_timestamp > exp_timestamp

    except Exception as e:
        logger.error(f"Error checking token expiration: {e}")
        return True


def get_token_expiration(token: str) -> Optional[datetime]:
    """
    Get token expiration time without verification

    Args:
        token: JWT token string

    Returns:
        Expiration datetime if available, None otherwise
    """
    try:
        payload = decode_token_payload(token)
        exp_timestamp = payload.get("exp")

        if exp_timestamp is None:
            return None

        return datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)

    except Exception as e:
        logger.error(f"Error getting token expiration: {e}")
        return None