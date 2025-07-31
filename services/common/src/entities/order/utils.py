"""
Order utility functions and status management.
Keeps order models clean by separating business logic.
"""

from enum import Enum
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Set, Tuple
from decimal import Decimal
from pydantic import BaseModel, Field

from .enums import OrderStatus, OrderType


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
                           limit_price: Optional[Decimal] = None,
                           price_per_unit: Optional[Decimal] = None) -> Tuple[bool, Optional[str]]:
        """Validate minimum order value for buy orders"""
        if order_type in [OrderType.MARKET_BUY, OrderType.LIMIT_BUY]:
            # Estimate value using available price
            estimated_price = limit_price or price_per_unit or Decimal("50000")  # Default BTC price
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
                                       limit_price: Optional[Decimal] = None,
                                       price_per_unit: Optional[Decimal] = None,
                                       stop_price: Optional[Decimal] = None) -> Tuple[bool, Optional[str]]:
        """Validate order type specific requirements"""

        if order_type in [OrderType.LIMIT_BUY, OrderType.LIMIT_SELL]:
            if limit_price is None:
                return False, f"{order_type} orders require a limit_price"
            if price_per_unit is None:
                return False, f"{order_type} orders require a price_per_unit"

        elif order_type in [OrderType.STOP_LOSS, OrderType.TAKE_PROFIT]:
            if stop_price is None:
                return False, f"{order_type} orders require a stop_price"

        elif order_type in [OrderType.MARKET_BUY, OrderType.MARKET_SELL]:
            if price_per_unit is not None:
                return False, f"{order_type} orders should not specify price_per_unit"
            if limit_price is not None:
                return False, f"{order_type} orders should not specify limit_price"

        return True, None


class OrderBusinessRules:
    """Business rule validation for orders"""

    @classmethod
    def validate_all_business_rules(cls, order_type: OrderType, quantity: Decimal,
                                  limit_price: Optional[Decimal] = None,
                                  price_per_unit: Optional[Decimal] = None,
                                  stop_price: Optional[Decimal] = None,
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
        if limit_price:
            is_valid, error = OrderValidationUtils.validate_price_precision(limit_price)
            if not is_valid:
                errors.append(error)

        if price_per_unit:
            is_valid, error = OrderValidationUtils.validate_price_precision(price_per_unit)
            if not is_valid:
                errors.append(error)

        # Order type requirements
        is_valid, error = OrderValidationUtils.validate_order_type_requirements(
            order_type, limit_price, price_per_unit, stop_price
        )
        if not is_valid:
            errors.append(error)

        # Order value validation
        is_valid, error = OrderValidationUtils.validate_order_value(
            order_type, quantity, limit_price, price_per_unit
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