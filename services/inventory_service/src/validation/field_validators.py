"""
Inventory Service Field Validators

Only validates API request fields (GET endpoints only).
Combines sanitization + format validation in each function.
"""

import re

# Import proper exceptions
from inventory_exceptions import CNOPAssetValidationException

# Import shared validation functions from common module
from common.core.validation.shared_validators import (
    sanitize_string,
    is_suspicious
)


# sanitize_string and is_suspicious are now imported from common module


def validate_asset_id(v: str) -> str:
    """
    Inventory service: asset_id validation (path parameter)
    Combines sanitization + format validation
    """
    if not v:
        raise CNOPAssetValidationException("Asset ID cannot be empty")

    # 1. Check for suspicious content first
    if is_suspicious(v):
        raise CNOPAssetValidationException("Asset ID contains potentially malicious content")

    # 2. Basic sanitization (remove HTML tags, trim whitespace)
    v = sanitize_string(v)

    # 3. Check for empty after sanitization
    if not v:
        raise CNOPAssetValidationException("Asset ID cannot be empty")

    # 4. Format validation - asset IDs should be alphanumeric, 1-10 chars
    if not re.match(r'^[a-zA-Z0-9]{1,10}$', v):
        raise CNOPAssetValidationException("Asset ID must be 1-10 alphanumeric characters")

    # 5. Convert to uppercase for consistency
    return v.upper()