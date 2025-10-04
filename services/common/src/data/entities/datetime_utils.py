"""
Datetime utility functions for entity conversions
"""
from datetime import datetime, timezone
from typing import Optional


def safe_parse_datetime(dt_str: Optional[str]) -> datetime:
    """
    Safely parse a datetime string, falling back to current UTC time if invalid/None

    Args:
        dt_str: ISO datetime string or None

    Returns:
        Parsed datetime object or current UTC time
    """
    if not dt_str:
        return datetime.now(timezone.utc)

    try:
        # Handle both 'Z' and '+00:00' timezone formats
        normalized_str = dt_str.replace('Z', '+00:00')
        return datetime.fromisoformat(normalized_str)
    except (ValueError, AttributeError):
        return datetime.now(timezone.utc)


def get_current_utc() -> datetime:
    """Get current UTC datetime"""
    return datetime.now(timezone.utc)
