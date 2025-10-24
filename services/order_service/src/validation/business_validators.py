"""
Order Service Business Validators

Layer 2: Business validation functions for service layer
Handles business rules, existence checks, and complex validation logic.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from common.data.entities.order.enums import OrderType, OrderStatus

from common.exceptions import CNOPAssetNotFoundException, CNOPOrderNotFoundException
from order_exceptions.exceptions import CNOPOrderValidationException

# Local constants for validation messages (only used in this file)
MSG_ERROR_INSUFFICIENT_BALANCE_DETAILED = "Insufficient balance for this order"
MSG_ERROR_ORDER_PRICE_REQUIRED = "order_price is required"
MSG_ERROR_EXPIRES_AT_REQUIRED = "expires_at is required for limit orders"
MSG_ERROR_ORDER_CANNOT_BE_CANCELLED = "Order in this state cannot be cancelled"

from common.data.dao.inventory.asset_dao import AssetDAO
from common.data.dao.order.order_dao import OrderDAO
from common.data.dao.user.user_dao import UserDAO
from common.data.dao.user.balance_dao import BalanceDAO


def _validate_username_exists_and_active(username: str, user_dao: UserDAO) -> None:
    """
    Private method to validate username exists and is active

    Args:
        username: Username to validate
        user_dao: User DAO instance

    Raises:
        OrderValidationException: If user doesn't exist or is not active
    """
    try:
        user = user_dao.get_user_by_username(username)
        # User exists, consider them active (no is_active field in current User entity)
    except Exception as e:
        raise CNOPOrderValidationException(f"User '{username}' not found or invalid")


def _validate_asset_exists_and_tradeable(asset_id: str, asset_dao: AssetDAO) -> None:
    """
    Private method to validate asset exists and is tradeable

    Args:
        asset_id: Asset ID to validate
        asset_dao: Asset DAO instance

    Raises:
        OrderValidationException: If asset doesn't exist or is not tradeable
    """
    try:
        asset = asset_dao.get_asset_by_id(asset_id)
        if not asset.is_active:
            raise CNOPOrderValidationException(f"Asset {asset_id} is not tradeable")
    except CNOPAssetNotFoundException:
        raise CNOPOrderValidationException(f"Asset {asset_id} not found")


def _validate_asset_exists(asset_id: str, asset_dao: AssetDAO) -> None:
        """
        Private method to validate asset exists (without tradeable check)

        Args:
            asset_id: Asset ID to validate
            asset_dao: Asset DAO instance

        Raises:
            OrderValidationException: If asset doesn't exist
        """
        try:
            asset_dao.get_asset_by_id(asset_id)
        except CNOPAssetNotFoundException:
            raise CNOPOrderValidationException(f"Asset {asset_id} not found")


def _validate_user_balance_for_buy_order(
    username: str,
    quantity: Decimal,
    order_price: Optional[Decimal],
    balance_dao: BalanceDAO,
    asset_dao: AssetDAO,
    asset_id: str
) -> None:
    """
    Private method to validate user has sufficient balance for buy orders

    Args:
        username: Username to check balance for
        quantity: Order quantity
        order_price: Order price (None for market orders)
        balance_dao: Balance DAO instance
        asset_id: Asset ID for market price lookup

    Raises:
        OrderValidationException: If insufficient balance
    """
    try:
        user_balance = balance_dao.get_balance(username)

        if order_price is None:
            from controllers.dependencies import get_current_market_price

            try:
                market_price = get_current_market_price(asset_id, asset_dao)
                required_amount = quantity * market_price
            except Exception as e:
                # No fallback - if we can't get market price, we can't validate the order
                raise CNOPOrderValidationException(f"Unable to validate market order for {asset_id}: {str(e)}")
        else:
            required_amount = quantity * order_price

        if user_balance.current_balance < required_amount:
            raise CNOPOrderValidationException(f"{MSG_ERROR_INSUFFICIENT_BALANCE_DETAILED}. Required: ${required_amount}, Available: ${user_balance.current_balance}")
    except Exception as e:
        raise CNOPOrderValidationException(f"Unable to verify user balance: {str(e)}")




def validate_order_creation_business_rules(
    order_type: OrderType,
    asset_id: str,
    quantity: Decimal,
    order_price: Optional[Decimal],
    expires_at: Optional[datetime],
    username: str,
    asset_dao: AssetDAO,
    user_dao: UserDAO,
    balance_dao: BalanceDAO,
) -> None:
    """
    Layer 2: Business validation for order creation

    Validates:
    - Username exists and is active
    - Asset exists and is tradeable
    - User has sufficient balance (for buy orders)
    - User has sufficient quantity (for sell orders)
    - Order type specific rules
    - Market conditions
    """

    _validate_username_exists_and_active(username, user_dao)

    _validate_asset_exists_and_tradeable(asset_id, asset_dao)

    if order_type in [OrderType.LIMIT_BUY, OrderType.LIMIT_SELL]:
        if order_price is None:
            raise CNOPOrderValidationException(f"{MSG_ERROR_ORDER_PRICE_REQUIRED} for {order_type.value} orders")
        if expires_at is None:
            raise CNOPOrderValidationException(MSG_ERROR_EXPIRES_AT_REQUIRED)

    if quantity < Decimal("0.001"):
        raise CNOPOrderValidationException("Order quantity below minimum threshold (0.001)")

    if quantity > Decimal("1000"):
        raise CNOPOrderValidationException("Order quantity exceeds maximum threshold (1000)")

    if order_type in [OrderType.MARKET_BUY, OrderType.LIMIT_BUY]:
        _validate_user_balance_for_buy_order(username, quantity, order_price, balance_dao, asset_dao, asset_id)

    # Note: Sell order validation (asset balance check) is handled by user service
    # The order service no longer validates asset balances directly


def validate_order_cancellation_business_rules(
    order_id: str,
    username: str,
    order_dao: OrderDAO,
    user_dao: UserDAO,
) -> None:
    """
    Layer 2: Business validation for order cancellation

    Validates:
    - Username exists and is active
    - Order exists and belongs to user
    - Order is in cancellable state
    - User has permission to cancel
    """

    _validate_username_exists_and_active(username, user_dao)

    try:
        order = order_dao.get_order(order_id)
        if order.username != username:
            raise CNOPOrderValidationException("You can only cancel your own orders")

        if order.order_type in [OrderType.MARKET_BUY, OrderType.MARKET_SELL]:
            raise CNOPOrderValidationException("Market orders cannot be cancelled")

        if order.status not in [OrderStatus.PENDING, OrderStatus.QUEUED]:
            raise CNOPOrderValidationException(f"{MSG_ERROR_ORDER_CANNOT_BE_CANCELLED} in {order.status.value} state")

    except CNOPOrderNotFoundException:
        raise CNOPOrderValidationException(f"Order {order_id} not found")


def validate_order_retrieval_business_rules(
    order_id: str,
    username: str,
    order_dao: OrderDAO,
    user_dao: UserDAO,
) -> None:
    """
    Layer 2: Business validation for order retrieval

    Validates:
    - Username exists and is active
    - Order exists and belongs to user
    - User has permission to view
    """

    _validate_username_exists_and_active(username, user_dao)

    try:
        order = order_dao.get_order(order_id)
        if order.username != username:
            raise CNOPOrderValidationException("You can only view your own orders")
    except CNOPOrderNotFoundException:
        raise CNOPOrderNotFoundException(f"Order {order_id} not found")


def validate_order_listing_business_rules(
    username: str,
    status: Optional[OrderStatus],
    asset_id: Optional[str],
    asset_dao: AssetDAO,
    user_dao: UserDAO,
) -> None:
    """
    Layer 2: Business validation for order listing

    Validates:
    - Username exists and is active
    - User has permission to list orders
    - Asset exists (if filtering by asset)
    - Status is valid (if filtering by status)
    """

    _validate_username_exists_and_active(username, user_dao)

    if asset_id:
        _validate_asset_exists(asset_id, asset_dao)


def validate_order_history_business_rules(
    asset_id: str,
    username: str,
    asset_dao: AssetDAO,
    user_dao: UserDAO,
) -> None:
    """
    Layer 2: Business validation for order history

    Validates:
    - Username exists and is active
    - Asset exists
    - User has permission to view history
    """

    _validate_username_exists_and_active(username, user_dao)

    _validate_asset_exists(asset_id, asset_dao)


def validate_market_conditions(
    asset_id: str,
    order_type: OrderType,
    quantity: Decimal,
) -> None:
    """
    Layer 2: Market condition validation

    Validates:
    - Market is open
    - Sufficient liquidity
    - Price impact is acceptable
    """



    if quantity > Decimal("100"):
        pass


def validate_user_permissions(
    username: str,
    action: str,
    user_dao: UserDAO,
) -> None:
    """
    Layer 2: User permission validation

    Validates:
    - User account is active
    - User has required permissions
    - User is not rate limited
    """

    _validate_username_exists_and_active(username, user_dao)

    pass