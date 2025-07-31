"""
Order-related enums for the Order Processor system.
"""

from enum import Enum


class OrderType(str, Enum):
    """Order types for different trading strategies"""
    MARKET_BUY = "market_buy"
    MARKET_SELL = "market_sell"
    LIMIT_BUY = "limit_buy"
    LIMIT_SELL = "limit_sell"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"


class OrderStatus(str, Enum):
    """Order status flow for tracking order lifecycle"""
    PENDING = "pending"           # Order created, awaiting validation
    CONFIRMED = "confirmed"       # Order validated, ready for processing
    QUEUED = "queued"            # Limit order waiting for price conditions
    TRIGGERED = "triggered"      # Limit order conditions met, ready to process
    PROCESSING = "processing"    # Order being executed
    COMPLETED = "completed"      # Order successfully executed
    CANCELLED = "cancelled"      # Order cancelled by user
    FAILED = "failed"           # Order failed during processing
    EXPIRED = "expired"         # Limit order expired without execution