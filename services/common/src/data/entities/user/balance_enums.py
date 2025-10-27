"""
Balance-related enums for user service.
"""

from enum import Enum


class TransactionType(str, Enum):
    """Types of balance transactions."""
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    ORDER_PAYMENT = "order_payment"
    ORDER_SALE = "order_sale"  # Cash from selling assets
    SYSTEM_ADJUSTMENT = "system_adjustment"


class TransactionStatus(str, Enum):
    """Status of balance transactions."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Default values
DEFAULT_TRANSACTION_STATUS = TransactionStatus.PENDING
VALID_TRANSACTION_TYPES = [t.value for t in TransactionType]
VALID_TRANSACTION_STATUSES = [s.value for s in TransactionStatus]