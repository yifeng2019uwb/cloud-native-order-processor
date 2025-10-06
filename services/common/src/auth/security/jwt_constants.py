#!/usr/bin/env python3
"""
JWT configuration constants.

Centralizes all JWT-related constants to avoid hardcoded values.
"""


class JWTConfig:
    """JWT configuration constants"""

    # JWT field names
    USERNAME = "username"
    SUBJECT = "sub"
    ROLE = "role"
    EXPIRATION = "exp"
    ISSUED_AT = "iat"
    TYPE = "type"
    ISSUER = "iss"
    AUDIENCE = "aud"
    METADATA = "metadata"

    # JWT values
    ACCESS_TOKEN_TYPE = "access_token"
    TOKEN_TYPE_BEARER = "bearer"
    ALGORITHM_HS256 = "HS256"

    JWT_SECRET_KEY = "JWT_SECRET_KEY"
    DEFAULT_EXPIRATION_HOURS = 1
    SECONDS_PER_HOUR = 3600

    # Response field names
    ACCESS_TOKEN = "access_token"
    TOKEN_TYPE = "token_type"
    EXPIRES_IN = "expires_in"
    EXPIRES_AT = "expires_at"

    # Default values
    DEFAULT_SECRET = "dev-secret-key-change-in-production"
    DEFAULT_EXPIRATION_HOURS = 1
    SECONDS_PER_HOUR = 3600

    # JWT decode options
    VERIFY_SIGNATURE = "verify_signature"
