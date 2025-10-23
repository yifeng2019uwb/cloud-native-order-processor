#!/usr/bin/env python3
"""
JWT configuration constants.

Centralizes all JWT-related constants to avoid hardcoded values.
"""


class JWTConfig:
    """JWT configuration constants"""
    # Token types
    ACCESS_TOKEN_TYPE = "access_token"
    TOKEN_TYPE_BEARER = "bearer"

    # Algorithm
    ALGORITHM_HS256 = "HS256"

    # Environment variable names
    JWT_SECRET_KEY = "JWT_SECRET_KEY"

    # Time configuration
    DEFAULT_EXPIRATION_HOURS = 1
    SECONDS_PER_HOUR = 3600

    # JWT decode options
    VERIFY_SIGNATURE = "verify_signature"

class JwtFields:
    """JWT field names"""
    USERNAME = "username"
    SUBJECT = "sub"
    ROLE = "role"
    EXPIRATION = "exp"
    ISSUED_AT = "iat"
    TYPE = "type"
    TOKEN_TYPE = "token_type"  # Different from TYPE - used in some token payloads
    ISSUER = "iss"
    AUDIENCE = "aud"
    METADATA = "metadata"

class JwtResponseFields:
    """Response field names"""
    ACCESS_TOKEN = "access_token"
    TOKEN_TYPE = "token_type"
    EXPIRES_IN = "expires_in"
    EXPIRES_AT = "expires_at"

class TokenErrorTypes:
    """Error types for token validation"""
    TOKEN_EXPIRED = "token_expired"
    TOKEN_INVALID = "token_invalid"
    VALIDATION_ERROR = "validation_error"

class TokenTypes:
    """Token type constants"""
    ACCESS = "access"
    REFRESH = "refresh"
    SCOPE = "scope"

class RequestDefaults:
    """Default values for requests"""
    EMPTY_STRING = ""
    EMPTY_DICT = {}
    REQUEST_ID_PREFIX = "req-"
