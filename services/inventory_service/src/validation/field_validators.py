"""
Inventory Service Field Validators

Only validates API request fields (GET endpoints only).
Combines sanitization + format validation in each function.
"""

import re

# Import proper exceptions
from inventory_exceptions import CNOPAssetValidationException

# Local constants for validation error messages
MSG_ERROR_ASSET_ID_EMPTY = "Asset ID cannot be empty"
MSG_ERROR_ASSET_ID_MALICIOUS = "Asset ID contains potentially malicious content"
MSG_ERROR_ASSET_ID_INVALID_FORMAT = "Asset ID must be 1-10 alphanumeric characters"

# Import shared validation functions from common module
from common.core.validation.shared_validators import (
    sanitize_string,
    is_suspicious
)


def validate_asset_id(v: str) -> str:
    """
    Inventory service: asset_id validation (path parameter)
    Combines sanitization + format validation
    """
    if not v:
        raise CNOPAssetValidationException(MSG_ERROR_ASSET_ID_EMPTY)

    # 1. Check for suspicious content first
    if is_suspicious(v):
        raise CNOPAssetValidationException(MSG_ERROR_ASSET_ID_MALICIOUS)

    # 2. Basic sanitization (remove HTML tags, trim whitespace)
    v = sanitize_string(v)

    # 3. Check for empty after sanitization
    if not v:
        raise CNOPAssetValidationException(MSG_ERROR_ASSET_ID_EMPTY)

    # 4. Format validation - asset IDs should be alphanumeric, 1-10 chars
    if not re.match(r'^[a-zA-Z0-9]{1,10}$', v):
        raise CNOPAssetValidationException(MSG_ERROR_ASSET_ID_INVALID_FORMAT)

    # 5. Convert to uppercase for consistency
    return v.upper()