"""
JWT Token utilities for user authentication
"""
import os
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
import logging

logger = logging.getLogger(__name__)

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24


def create_access_token(email: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token for authenticated user

    Args:
        email: User's email address
        expires_delta: Optional custom expiration time

    Returns:
        JWT token string
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)

    payload = {
        "sub": email,  # Subject (user identifier)
        "exp": expire,  # Expiration time
        "iat": datetime.utcnow(),  # Issued at
        "type": "access_token"
    }

    try:
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        logger.info(f"Access token created for user: {email}")
        return token
    except Exception as e:
        logger.error(f"Error creating access token: {e}")
        raise


def verify_access_token(token: str) -> Optional[str]:
    """
    Verify JWT access token and extract user email

    Args:
        token: JWT token string

    Returns:
        User email if token is valid, None otherwise

    Raises:
        JWTError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        # Check token type
        if payload.get("type") != "access_token":
            logger.warning("Invalid token type")
            raise JWTError("Invalid token type")

        # Extract email
        email: str = payload.get("sub")
        if email is None:
            logger.warning("Token missing subject (email)")
            raise JWTError("Token missing subject")

        logger.debug(f"Token verified for user: {email}")
        return email

    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        raise JWTError("Token expired")
    except jwt.InvalidTokenError:
        logger.warning("Invalid token provided")
        raise JWTError("Invalid token")
    except Exception as e:
        logger.error(f"Unexpected error verifying token: {e}")
        raise JWTError("Token verification failed")


def decode_token_payload(token: str) -> dict:
    """
    Decode token payload without verification (for debugging)

    Args:
        token: JWT token string

    Returns:
        Token payload as dictionary
    """
    try:
        # Decode without verification for debugging
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload
    except Exception as e:
        logger.error(f"Error decoding token payload: {e}")
        return {}


def is_token_expired(token: str) -> bool:
    """
    Check if token is expired without full verification

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

        exp_datetime = datetime.fromtimestamp(exp_timestamp)
        return datetime.utcnow() > exp_datetime

    except Exception:
        return True


def get_token_expiration(token: str) -> Optional[datetime]:
    """
    Get token expiration datetime

    Args:
        token: JWT token string

    Returns:
        Expiration datetime or None if invalid
    """
    try:
        payload = decode_token_payload(token)
        exp_timestamp = payload.get("exp")

        if exp_timestamp is None:
            return None

        return datetime.fromtimestamp(exp_timestamp)

    except Exception:
        return None