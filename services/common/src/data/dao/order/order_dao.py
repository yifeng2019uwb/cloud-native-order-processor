"""
Order DAO for database operations.
Handles CRUD operations for Order entities using PynamoDB.
"""

from datetime import datetime, timezone
from typing import List

from ....exceptions import CNOPEntityValidationException
from ....exceptions.shared_exceptions import CNOPOrderNotFoundException
from ....shared.logging import BaseLogger, LogAction, LoggerName
from ...entities.order import Order, OrderItem
from ...entities.order.enums import OrderStatus
from ...exceptions import CNOPDatabaseOperationException
from ...entities.entity_constants import OrderFields

logger = BaseLogger(LoggerName.DATABASE, log_to_file=True)


class OrderDAO:
    """Data Access Object for Order entities"""

    def __init__(self):
        """Initialize Order DAO"""
        pass

    def create_order(self, order: Order) -> Order:
        """
        Create a new order in the database.

        Args:
            order: Order entity to create

        Returns:
            Created order

        Raises:
            CNOPDatabaseOperationException: If database operation fails
        """
        try:
            # Convert Order entity to OrderItem for database storage
            order_item = OrderItem.from_order(order)

            # Save to database
            logger.info(
                action=LogAction.DB_OPERATION,
                message=f"Creating order: id={order.order_id}, user={order.username}, "
                       f"asset={order.asset_id}, type={order.order_type.value}"
            )
            order_item.save()

            logger.info(
                action=LogAction.DB_OPERATION,
                message=f"Order created successfully: id={order.order_id}, user={order.username}, "
                       f"asset={order.asset_id}, type={order.order_type.value}"
            )
            return order

        except Exception as e:
            logger.error(
                action=LogAction.ERROR,
                message=f"Failed to create order '{order.order_id}': {str(e)}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while creating order '{order.order_id}': {str(e)}") from e

    def get_order(self, order_id: str) -> Order:
        """
        Get order by ID.

        Args:
            order_id: Order ID to retrieve

        Returns:
            Order entity if found

        Raises:
            CNOPOrderNotFoundException: If order not found
            CNOPDatabaseOperationException: If database operation fails
        """
        try:
            # Get order from database
            order_item = OrderItem.get(order_id, OrderFields.SK_VALUE)
            return order_item.to_order()

        except OrderItem.DoesNotExist:
            raise CNOPOrderNotFoundException(f"Order '{order_id}' not found")
        except Exception as e:
            logger.error(
                action=LogAction.ERROR,
                message=f"Failed to get order '{order_id}': {str(e)}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while retrieving order '{order_id}': {str(e)}") from e


    def get_orders_by_user(self, username: str, limit: int = 50, offset: int = 0) -> List[Order]:
        """
        Get all orders for a user.

        Args:
            username: Username to get orders for
            limit: Maximum number of orders to return
            offset: Number of orders to skip

        Returns:
            List of orders

        Raises:
            CNOPDatabaseOperationException: If database operation fails
        """
        try:
            logger.info(
                action=LogAction.DB_OPERATION,
                message=f"Retrieving orders for user: username={username}, limit={limit}, offset={offset}"
            )

            # Query using GSI - query by username (GSI_PK) only
            order_items = OrderItem.user_orders_index.query(
                username,
                scan_index_forward=False,  # Most recent first
                limit=limit
            )

            # Convert to Order entities
            orders = [order_item.to_order() for order_item in order_items]

            # Apply offset (PynamoDB doesn't support offset directly)
            if offset > 0:
                orders = orders[offset:]

            logger.info(
                action=LogAction.DB_OPERATION,
                message=f"Retrieved {len(orders)} orders for user '{username}'"
            )

            return orders

        except Exception as e:
            logger.error(
                action=LogAction.ERROR,
                message=f"Failed to get orders for user '{username}': {str(e)}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while retrieving orders for user '{username}': {str(e)}") from e


    def update_order_status(self, order_id: str, new_status: OrderStatus, reason: str = None) -> Order:
        """
        Update order status with optional reason.

        Args:
            order_id: Order ID to update
            new_status: New status to set
            reason: Optional reason for status change

        Returns:
            Updated order

        Raises:
            CNOPOrderNotFoundException: If order not found
            CNOPDatabaseOperationException: If database operation fails
        """
        try:
            logger.info(
                action=LogAction.DB_OPERATION,
                message=f"Updating order status: id={order_id}, new_status={new_status.value}, reason={reason or 'none'}"
            )

            # Get existing order
            order_item = OrderItem.get(order_id, OrderFields.SK_VALUE)

            # Update status and reason
            order_item.status = new_status.value
            if reason:
                order_item.status_reason = reason

            # Save with updated timestamp
            order_item.save()

            logger.info(
                action=LogAction.DB_OPERATION,
                message=f"Order status updated successfully: id={order_id}, new_status={new_status.value}, reason={reason or 'none'}"
            )

            return order_item.to_order()

        except OrderItem.DoesNotExist:
            logger.warning(
                action=LogAction.ERROR,
                message=f"Order '{order_id}' not found for status update"
            )
            raise CNOPOrderNotFoundException(f"Order '{order_id}' not found")

        except Exception as e:
            logger.error(
                action=LogAction.ERROR,
                message=f"Failed to update order status '{order_id}': {str(e)}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while updating order status for order '{order_id}': {str(e)}") from e

    def order_exists(self, order_id: str) -> bool:
        """
        Check if order exists.

        Args:
            order_id: Order ID to check

        Returns:
            True if order exists, False otherwise

        Raises:
            CNOPDatabaseOperationException: If database operation fails
        """
        try:
            logger.info(
                action=LogAction.DB_OPERATION,
                message=f"Checking if order exists: id={order_id}"
            )

            # Try to get the order
            OrderItem.get(order_id, OrderFields.SK_VALUE)
            return True

        except OrderItem.DoesNotExist:
            return False

        except Exception as e:
            logger.error(
                action=LogAction.ERROR,
                message=f"Failed to check if order '{order_id}' exists: {str(e)}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while checking existence of order '{order_id}': {str(e)}") from e
