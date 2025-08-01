"""
Core order entity model.
Contains the main Order class for database operations.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime, timezone
from decimal import Decimal

from .enums import OrderType, OrderStatus
from .utils import OrderStatusManager, OrderStatusTransition


class Order(BaseModel):
    """Core order entity model for DynamoDB storage

    Database Schema:
    - PK: order_id (Primary Key)
    - SK: created_at (Sort Key for time-based queries)
    - GSI2-PK: user_id (Global Secondary Index Partition Key)
    - GSI2-SK: asset_id#status#created_at (Composite Sort Key for filtering)

    Query Patterns:
    - Get specific order: PK = order_id
    - Get user's all orders: GSI2-PK = user_id
    - Get user's BTC orders: GSI2-PK = user_id, GSI2-SK begins_with "BTC#"
    - Get user's pending BTC orders: GSI2-PK = user_id, GSI2-SK begins_with "BTC#pending#"
    """

    order_id: str = Field(
        ...,
        description="Primary Key - Unique order identifier"
    )

    user_id: str = Field(
        ...,
        description="GSI2 Partition Key - User who placed the order"
    )

    order_type: OrderType = Field(
        ...,
        description="Type of order"
    )

    status: OrderStatus = Field(
        ...,
        description="Current order status"
    )

    asset_id: str = Field(
        ...,
        description="Asset symbol being traded"
    )

    quantity: Decimal = Field(
        ...,
        description="Amount of asset to trade"
    )

    order_price: Optional[Decimal] = Field(
        None,
        description="Price for limit orders, None for market orders"
    )

    total_amount: Decimal = Field(
        ...,
        description="Total order value"
    )

    executed_quantity: Decimal = Field(
        default=0,
        description="Amount of asset already executed"
    )

    executed_price: Optional[Decimal] = Field(
        None,
        description="Average execution price"
    )

    currency: str = Field(
        default="USD",
        description="Order currency"
    )

    expires_at: Optional[datetime] = Field(
        None,
        description="Expiration time for limit orders"
    )

    created_at: datetime = Field(
        ...,
        description="Sort Key - Order creation timestamp for time-based queries"
    )

    updated_at: datetime = Field(
        ...,
        description="Last update timestamp"
    )

    completed_at: Optional[datetime] = Field(
        None,
        description="Order completion timestamp"
    )

    status_history: List[OrderStatusTransition] = Field(
        default_factory=list,
        description="Order status change history"
    )

    @property
    def is_completed(self) -> bool:
        """Check if order is completed"""
        return self.status == OrderStatus.COMPLETED

    @property
    def is_cancelled(self) -> bool:
        """Check if order is cancelled"""
        return self.status in [OrderStatus.CANCELLED, OrderStatus.FAILED, OrderStatus.EXPIRED]

    @property
    def is_active(self) -> bool:
        """Check if order is still active"""
        return OrderStatusManager.is_active_status(self.status)

    @property
    def remaining_quantity(self) -> Decimal:
        """Calculate remaining quantity to execute"""
        return self.quantity - self.executed_quantity

    @property
    def is_fully_executed(self) -> bool:
        """Check if order is fully executed"""
        return self.executed_quantity >= self.quantity

    @property
    def execution_percentage(self) -> Decimal:
        """Calculate execution percentage (0-100)"""
        if self.quantity == 0:
            return Decimal("0")
        return (self.executed_quantity / self.quantity) * Decimal("100")

    @property
    def average_execution_price(self) -> Optional[Decimal]:
        """Calculate average execution price if executed"""
        if self.executed_quantity > 0 and self.executed_price:
            return self.executed_price
        return None

    @property
    def is_terminal(self) -> bool:
        """Check if order is in terminal status"""
        return OrderStatusManager.is_terminal_status(self.status)

    @property
    def can_be_cancelled_by_user(self) -> bool:
        """Check if user can cancel this order"""
        return OrderStatusManager.can_user_cancel(self.status)

    def can_transition_to(
        self,
        new_status: OrderStatus,
        user_id: Optional[str] = None,
        is_system: bool = False
    ) -> tuple[bool, Optional[str]]:
        """Check if order can transition to new status"""
        return OrderStatusManager.validate_transition(
            self.status,
            new_status,
            user_id,
            is_system
        )

    def transition_to(
        self,
        new_status: OrderStatus,
        reason: Optional[str] = None,
        changed_by: Optional[str] = None,
        is_system: bool = False,
        context: Optional[dict] = None
    ) -> bool:
        """
        Transition order to new status with validation
        Returns True if successful, raises exception if invalid
        """

        # Validate transition
        is_valid, error_msg = self.can_transition_to(
            new_status,
            changed_by,
            is_system
        )

        if not is_valid:
            raise ValueError(f"Invalid status transition: {error_msg}")

        # Record the transition
        transition = OrderStatusTransition(
            from_status=self.status,
            to_status=new_status,
            reason=reason,
            changed_by=changed_by or "system",
            context=context or {}
        )

        # Update order
        old_status = self.status
        self.status = new_status
        self.updated_at = datetime.now(timezone.utc)
        self.status_history.append(transition)

        # Set completion timestamp for terminal states
        if new_status == OrderStatus.COMPLETED and not self.completed_at:
            self.completed_at = datetime.now(timezone.utc)

        return True

    def get_status_transitions(self) -> List[OrderStatusTransition]:
        """Get complete status transition history"""
        return self.status_history.copy()

    def get_last_transition(self) -> Optional[OrderStatusTransition]:
        """Get most recent status transition"""
        return self.status_history[-1] if self.status_history else None



    def validate_order_state(self) -> List[str]:
        """Validate order state for business rules"""
        errors = []

        # Check executed quantity doesn't exceed total
        if self.executed_quantity > self.quantity:
            errors.append("Executed quantity cannot exceed total quantity")

        # Check execution price is set when executed
        if self.executed_quantity > 0 and not self.executed_price:
            errors.append("Execution price must be set when order is partially executed")

        # Check completion timestamp is set for completed orders
        if self.status == OrderStatus.COMPLETED and not self.completed_at:
            errors.append("Completion timestamp must be set for completed orders")

        return errors

    @property
    def gsi2_sort_key(self) -> str:
        """Generate GSI2 sort key for DynamoDB queries"""
        return f"{self.asset_id}#{self.status.value}#{self.created_at.isoformat()}"

    @property
    def gsi2_asset_prefix(self) -> str:
        """Generate asset prefix for GSI2 queries (e.g., 'BTC#')"""
        return f"{self.asset_id}#"

    @property
    def gsi2_asset_status_prefix(self) -> str:
        """Generate asset+status prefix for GSI2 queries (e.g., 'BTC#pending#')"""
        return f"{self.asset_id}#{self.status.value}#"

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "order_id": "ord_123456789",
                "user_id": "user_123",
                "order_type": "market_buy",
                "status": "completed",
                "asset_id": "BTC",
                "quantity": 0.5,
                "order_price": None,
                "total_amount": 22500.00,
                "executed_quantity": 0.5,
                "executed_price": 45000.00,
                "currency": "USD",
                "expires_at": None,
                "created_at": "2025-07-30T10:30:00Z",
                "updated_at": "2025-07-30T10:35:00Z",
                "completed_at": "2025-07-30T10:35:00Z"
            }
        }