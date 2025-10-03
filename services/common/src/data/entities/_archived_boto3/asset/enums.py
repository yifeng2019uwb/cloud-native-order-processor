"""
Asset Enums

This module contains enums for the Asset entities.
"""

from enum import Enum


class AssetTransactionType(str, Enum):
    """Asset transaction type enumeration"""

    BUY = "BUY"
    """Buy transaction - acquiring assets"""

    SELL = "SELL"
    """Sell transaction - disposing assets"""


class AssetTransactionStatus(str, Enum):
    """Asset transaction status enumeration"""

    PENDING = "PENDING"
    """Transaction is pending execution"""

    COMPLETED = "COMPLETED"
    """Transaction has been completed successfully"""

    FAILED = "FAILED"
    """Transaction has failed"""