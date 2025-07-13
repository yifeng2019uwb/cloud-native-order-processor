"""
Integration Tests Constants
Centralized configuration for all constants used in integration tests
"""
import os

# Timeouts
class Timeouts:
    DEFAULT = 10
    SHORT = 5
    LONG = 30

# HTTP Status Codes
class StatusCodes:
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500

# Headers
class Headers:
    CONTENT_TYPE_JSON = {"Content-Type": "application/json"}
    AUTHORIZATION_BEARER = "Bearer {}"