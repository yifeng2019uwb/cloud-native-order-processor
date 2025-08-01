"""
Order utility functions and status management.
Keeps order models clean by separating business logic.
"""

import uuid
import time
from enum import Enum
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Set, Tuple
from decimal import Decimal
from pydantic import BaseModel, Field

from .enums import OrderStatus, OrderType
from ...exceptions.shared_exceptions import OrderValidationException


class OrderStatusTransition(BaseModel):
    """Track order status changes with audit trail"""
    from_status: OrderStatus
    to_status: OrderStatus
    reason: Optional[str] = Field(None, description="Reason for status change")
    changed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    changed_by: Optional[str] = Field(None, description="User ID or 'system'")
    context: Optional[Dict] = Field(default_factory=dict, description="Additional context")


class OrderStatusManager:
    """Manages valid order status transitions and business rules"""

    # Define valid status transitions
    VALID_TRANSITIONS: Dict[OrderStatus, Set[OrderStatus]] = {
        OrderStatus.PENDING: {
            OrderStatus.CONFIRMED,
            OrderStatus.CANCELLED,
            OrderStatus.FAILED
        },
        OrderStatus.CONFIRMED: {
            OrderStatus.QUEUED,
            OrderStatus.PROCESSING,  # Direct to processing for market orders
            OrderStatus.CANCELLED
        },
        OrderStatus.QUEUED: {
            OrderStatus.TRIGGERED,
            OrderStatus.CANCELLED,
            OrderStatus.EXPIRED
        },
        OrderStatus.TRIGGERED: {
            OrderStatus.PROCESSING,
            OrderStatus.FAILED
        },
        OrderStatus.PROCESSING: {
            OrderStatus.COMPLETED,
            OrderStatus.FAILED
        },
        # Terminal states (no transitions out)
        OrderStatus.COMPLETED: set(),
        OrderStatus.CANCELLED: set(),
        OrderStatus.FAILED: set(),
        OrderStatus.EXPIRED: set(),
    }

    # Terminal statuses that cannot be changed
    TERMINAL_STATUSES = {
        OrderStatus.COMPLETED,
        OrderStatus.CANCELLED,
        OrderStatus.FAILED,
        OrderStatus.EXPIRED
    }

    # Active statuses that can be cancelled by user
    USER_CANCELLABLE_STATUSES = {
        OrderStatus.PENDING,
        OrderStatus.CONFIRMED,
        OrderStatus.QUEUED
    }

    @classmethod
    def can_transition(
        cls,
        from_status: OrderStatus,
        to_status: OrderStatus
    ) -> bool:
        """Check if status transition is valid"""
        return to_status in cls.VALID_TRANSITIONS.get(from_status, set())

    @classmethod
    def validate_transition(
        cls,
        from_status: OrderStatus,
        to_status: OrderStatus,
        user_id: Optional[str] = None,
        is_system: bool = False
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate status transition with business rules
        Returns: (is_valid, error_message)
        """

        # Check if transition is structurally valid
        if not cls.can_transition(from_status, to_status):
            return False, f"Invalid transition from {from_status} to {to_status}"

        # Check if order is in terminal state
        if from_status in cls.TERMINAL_STATUSES:
            return False, f"Cannot change status from terminal state {from_status}"

        # Check user cancellation permissions
        if to_status == OrderStatus.CANCELLED and not is_system:
            if from_status not in cls.USER_CANCELLABLE_STATUSES:
                return False, f"User cannot cancel order in {from_status} status"

        # Business rule: Only system can set FAILED status
        if to_status == OrderStatus.FAILED and not is_system:
            return False, "Only system can mark orders as failed"

        # Business rule: Only system can set EXPIRED status
        if to_status == OrderStatus.EXPIRED and not is_system:
            return False, "Only system can mark orders as expired"

        return True, None

    @classmethod
    def get_valid_transitions(cls, from_status: OrderStatus) -> Set[OrderStatus]:
        """Get all valid transitions from current status"""
        return cls.VALID_TRANSITIONS.get(from_status, set())

    @classmethod
    def is_terminal_status(cls, status: OrderStatus) -> bool:
        """Check if status is terminal (no further transitions)"""
        return status in cls.TERMINAL_STATUSES

    @classmethod
    def is_active_status(cls, status: OrderStatus) -> bool:
        """Check if order is in active (non-terminal) status"""
        return status not in cls.TERMINAL_STATUSES

    @classmethod
    def can_user_cancel(cls, status: OrderStatus) -> bool:
        """Check if user can cancel order in current status"""
        return status in cls.USER_CANCELLABLE_STATUSES


class OrderValidationUtils:
    """Utility functions for order validation"""

    # Configuration constants
    MIN_ORDER_QUANTITY = Decimal("0.001")
    MAX_ORDER_QUANTITY = Decimal("1000.0")
    MIN_ORDER_VALUE = Decimal("10.00")  # $10 minimum
    MAX_EXPIRATION_DAYS = 30
    MAX_DECIMAL_PLACES = 8  # For crypto quantities
    MAX_PRICE_DECIMAL_PLACES = 2  # For USD prices
    SUPPORTED_CURRENCIES = {"USD", "EUR", "GBP"}

    @classmethod
    def validate_quantity_range(cls, quantity: Decimal) -> Tuple[bool, Optional[str]]:
        """Validate quantity is within acceptable range"""
        if quantity < cls.MIN_ORDER_QUANTITY:
            return False, f"Order quantity {quantity} is below minimum threshold of {cls.MIN_ORDER_QUANTITY}"

        if quantity > cls.MAX_ORDER_QUANTITY:
            return False, f"Order quantity {quantity} exceeds maximum threshold of {cls.MAX_ORDER_QUANTITY}"

        return True, None

    @classmethod
    def validate_quantity_precision(cls, quantity: Decimal) -> Tuple[bool, Optional[str]]:
        """Validate quantity precision for crypto"""
        if quantity.as_tuple().exponent < -cls.MAX_DECIMAL_PLACES:
            return False, f"Quantity precision cannot exceed {cls.MAX_DECIMAL_PLACES} decimal places"
        return True, None

    @classmethod
    def validate_price_precision(cls, price: Decimal) -> Tuple[bool, Optional[str]]:
        """Validate price precision for USD"""
        if price.as_tuple().exponent < -cls.MAX_PRICE_DECIMAL_PLACES:
            return False, f"Price precision cannot exceed {cls.MAX_PRICE_DECIMAL_PLACES} decimal places"
        return True, None

    @classmethod
    def validate_order_value(cls, order_type: OrderType, quantity: Decimal,
                           order_price: Optional[Decimal] = None) -> Tuple[bool, Optional[str]]:
        """Validate minimum order value for buy orders"""
        if order_type in [OrderType.MARKET_BUY, OrderType.LIMIT_BUY]:
            # Estimate value using available price
            estimated_price = order_price or Decimal("50000")  # Default BTC price
            estimated_value = quantity * estimated_price

            if estimated_value < cls.MIN_ORDER_VALUE:
                return False, f"Order value must be at least ${cls.MIN_ORDER_VALUE}"

        return True, None

    @classmethod
    def validate_expiration_time(cls, expires_at: Optional[datetime]) -> Tuple[bool, Optional[str]]:
        """Validate expiration time is reasonable"""
        if not expires_at:
            return True, None

        current_time = datetime.now(timezone.utc)

        if expires_at <= current_time:
            return False, f"Expiration time {expires_at} must be in the future (current: {current_time})"

        max_expiration = current_time + timedelta(days=cls.MAX_EXPIRATION_DAYS)
        if expires_at > max_expiration:
            return False, f"Expiration time {expires_at} cannot be more than {cls.MAX_EXPIRATION_DAYS} days in the future"

        return True, None

    @classmethod
    def validate_currency(cls, currency: str) -> Tuple[bool, Optional[str]]:
        """Validate currency is supported"""
        if currency not in cls.SUPPORTED_CURRENCIES:
            return False, f"Currency {currency} is not supported. Supported currencies: {', '.join(cls.SUPPORTED_CURRENCIES)}"
        return True, None

    @classmethod
    def validate_order_type_requirements(cls, order_type: OrderType,
                                       order_price: Optional[Decimal] = None) -> Tuple[bool, Optional[str]]:
        """Validate order type specific requirements"""

        if order_type in [OrderType.LIMIT_BUY, OrderType.LIMIT_SELL]:
            if order_price is None:
                return False, f"{order_type} orders require an order_price"

        elif order_type in [OrderType.MARKET_BUY, OrderType.MARKET_SELL]:
            if order_price is not None:
                return False, f"{order_type} orders should not specify order_price"

        return True, None


class OrderBusinessRules:
    """Business rule validation for orders"""

    @classmethod
    def validate_all_business_rules(cls, order_type: OrderType, quantity: Decimal,
                                  order_price: Optional[Decimal] = None,
                                  expires_at: Optional[datetime] = None,
                                  currency: str = "USD") -> List[str]:
        """
        Validate all business rules for an order
        Returns list of error messages (empty if valid)
        """
        errors = []

        # Quantity validations
        is_valid, error = OrderValidationUtils.validate_quantity_range(quantity)
        if not is_valid:
            errors.append(error)

        is_valid, error = OrderValidationUtils.validate_quantity_precision(quantity)
        if not is_valid:
            errors.append(error)

        # Price validations
        if order_price:
            is_valid, error = OrderValidationUtils.validate_price_precision(order_price)
            if not is_valid:
                errors.append(error)

        # Order type requirements
        is_valid, error = OrderValidationUtils.validate_order_type_requirements(
            order_type, order_price
        )
        if not is_valid:
            errors.append(error)

        # Order value validation
        is_valid, error = OrderValidationUtils.validate_order_value(
            order_type, quantity, order_price
        )
        if not is_valid:
            errors.append(error)

        # Expiration validation
        is_valid, error = OrderValidationUtils.validate_expiration_time(expires_at)
        if not is_valid:
            errors.append(error)

        # Currency validation
        is_valid, error = OrderValidationUtils.validate_currency(currency)
        if not is_valid:
            errors.append(error)

        return errors


class OrderIdGenerator:
    """Generates unique order IDs with consistent format"""

    # Order ID prefix
    ORDER_PREFIX = "ord"

    # Separator for different ID components
    SEPARATOR = "_"

    @classmethod
    def generate_order_id(cls, user_id: Optional[str] = None) -> str:
        """
        Generate a unique order ID.

        Format: ord_YYYYMMDD_HHMMSS_UUID_SHORT
        Example: ord_20250730_143052_a1b2c3d4e5f6

        Args:
            user_id: Optional user ID for additional uniqueness

        Returns:
            Unique order ID string
        """
        # Get current timestamp
        now = datetime.now(timezone.utc)
        timestamp = now.strftime("%Y%m%d_%H%M%S")

        # Generate UUID and take first 12 characters
        unique_id = uuid.uuid4().hex[:12]

        # Build order ID
        order_id = f"{cls.ORDER_PREFIX}{cls.SEPARATOR}{timestamp}{cls.SEPARATOR}{unique_id}"

        # Add user ID if provided (for additional uniqueness)
        if user_id:
            order_id = f"{order_id}{cls.SEPARATOR}{user_id[:8]}"

        return order_id

    @classmethod
    def generate_simple_order_id(cls) -> str:
        """
        Generate a simple order ID without timestamp.

        Format: ord_UUID_SHORT
        Example: ord_a1b2c3d4e5f6

        Returns:
            Simple unique order ID string
        """
        unique_id = uuid.uuid4().hex[:12]
        return f"{cls.ORDER_PREFIX}{cls.SEPARATOR}{unique_id}"

    @classmethod
    def generate_timestamped_order_id(cls, user_id: Optional[str] = None) -> str:
        """
        Generate order ID with timestamp for better traceability.

        Format: ord_TIMESTAMP_UUID_SHORT
        Example: ord_1732891852_a1b2c3d4e5f6

        Args:
            user_id: Optional user ID for additional uniqueness

        Returns:
            Timestamped unique order ID string
        """
        # Unix timestamp
        timestamp = str(int(time.time()))

        # Generate UUID and take first 12 characters
        unique_id = uuid.uuid4().hex[:12]

        # Build order ID
        order_id = f"{cls.ORDER_PREFIX}{cls.SEPARATOR}{timestamp}{cls.SEPARATOR}{unique_id}"

        # Add user ID if provided
        if user_id:
            order_id = f"{order_id}{cls.SEPARATOR}{user_id[:8]}"

        return order_id

    @classmethod
    def parse_order_id(cls, order_id: str) -> dict:
        """
        Parse order ID to extract components.

        Args:
            order_id: Order ID to parse

        Returns:
            Dictionary with parsed components
        """
        if not order_id.startswith(cls.ORDER_PREFIX):
            raise OrderValidationException(f"Invalid order ID format: {order_id}")

        parts = order_id.split(cls.SEPARATOR)

        if len(parts) < 3:
            raise OrderValidationException(f"Invalid order ID format: {order_id}")

        result = {
            "prefix": parts[0],
            "unique_id": parts[-1] if len(parts) >= 3 else None
        }

        # Try to parse timestamp
        if len(parts) >= 3:
            try:
                # Check if it's a date format (YYYYMMDD_HHMMSS)
                if len(parts[1]) == 15 and parts[1].replace("_", "").isdigit():
                    date_str = parts[1]
                    result["date"] = date_str[:8]  # YYYYMMDD
                    result["time"] = date_str[9:]  # HHMMSS
                # Check if it's a unix timestamp
                elif parts[1].isdigit():
                    result["unix_timestamp"] = int(parts[1])
            except (ValueError, IndexError):
                pass

        # Check for user ID
        if len(parts) >= 4:
            result["user_id"] = parts[3]

        return result

    @classmethod
    def is_valid_order_id(cls, order_id: str) -> bool:
        """
        Validate order ID format.

        Args:
            order_id: Order ID to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            cls.parse_order_id(order_id)
            return True
        except OrderValidationException:
            return False

    @classmethod
    def get_order_id_info(cls, order_id: str) -> dict:
        """
        Get information about an order ID.

        Args:
            order_id: Order ID to analyze

        Returns:
            Dictionary with order ID information
        """
        if not cls.is_valid_order_id(order_id):
            return {"valid": False, "error": "Invalid order ID format"}

        try:
            parsed = cls.parse_order_id(order_id)
            info = {
                "valid": True,
                "format": "standard",
                "components": parsed
            }

            # Determine format type
            if "date" in parsed and "time" in parsed:
                info["format"] = "date_time"
            elif "unix_timestamp" in parsed:
                info["format"] = "timestamp"
            else:
                info["format"] = "simple"

            return info
        except Exception as e:
            return {"valid": False, "error": str(e)}