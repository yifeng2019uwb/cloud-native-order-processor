"""
Order DAO for database operations.
Handles CRUD operations for Order entities using DynamoDB.
"""

import logging
from typing import List, Optional
from decimal import Decimal
from datetime import datetime, timezone

from boto3.dynamodb.conditions import Key, Attr

from ..base_dao import BaseDAO
from ...entities.order import Order, OrderUpdate
from ...entities.order.enums import OrderStatus
from ...exceptions import (
    EntityNotFoundError,
    EntityAlreadyExistsError,
    BusinessRuleError,
    DatabaseOperationError
)

logger = logging.getLogger(__name__)


class OrderDAO(BaseDAO):
    """Data Access Object for Order entities"""

    def __init__(self, db_connection):
        """Initialize Order DAO with DynamoDB connection"""
        super().__init__(db_connection)

    def create_order(self, order: Order) -> Order:
        """
        Create a new order in the database.

        Args:
            order: Order entity to create

        Returns:
            Created order

        Raises:
            EntityAlreadyExistsError: If order with same ID already exists
            DatabaseOperationError: If database operation fails
        """
        try:
            # Check if order already exists
            if self.order_exists(order.order_id):
                raise EntityAlreadyExistsError(f"Order with ID {order.order_id} already exists")

            # Prepare item for DynamoDB
            item = order.model_dump()

            # Ensure timestamps are set
            now = datetime.now(timezone.utc)
            if not order.created_at:
                item['created_at'] = now.isoformat()
            if not order.updated_at:
                item['updated_at'] = now.isoformat()

            # Add GSI2 attributes
            item['GSI2-PK'] = order.user_id
            item['GSI2-SK'] = order.gsi2_sort_key

            # Insert into DynamoDB
            self.db.orders_table.put_item(Item=item)

            logger.info(f"Created order {order.order_id} for user {order.user_id}")
            return order

        except EntityAlreadyExistsError:
            raise
        except Exception as e:
            logger.error(f"Failed to create order {order.order_id}: {str(e)}")
            raise DatabaseOperationError(f"Failed to create order: {str(e)}")

    def get_order(self, order_id: str) -> Optional[Order]:
        """
        Get order by ID.

        Args:
            order_id: Order ID to retrieve

        Returns:
            Order entity if found, None otherwise

        Raises:
            DatabaseOperationError: If database operation fails
        """
        try:
            response = self.db.orders_table.get_item(
                Key={'order_id': order_id}
            )

            if 'Item' not in response:
                return None

            item = response['Item']
            return Order(**item)

        except Exception as e:
            logger.error(f"Failed to get order {order_id}: {str(e)}")
            raise DatabaseOperationError(f"Failed to get order: {str(e)}")

    def update_order(self, order_id: str, updates: OrderUpdate) -> Optional[Order]:
        """
        Update existing order (only status-related fields).

        Args:
            order_id: Order ID to update
            updates: OrderUpdate object with changes

        Returns:
            Updated order if successful, None if not found

        Raises:
            EntityNotFoundError: If order not found
            DatabaseOperationError: If database operation fails
        """
        try:
            # Get existing order
            existing_order = self.get_order(order_id)
            if not existing_order:
                raise EntityNotFoundError(f"Order {order_id} not found")

            # Prepare update expression
            update_expression = "SET updated_at = :updated_at"
            expression_values = {
                ':updated_at': datetime.now(timezone.utc).isoformat()
            }

            # Add status update if provided
            if updates.status is not None:
                update_expression += ", #status = :status"
                expression_values[':status'] = updates.status.value
                expression_values['#status'] = 'status'

            # Add executed quantity update if provided
            if updates.executed_quantity is not None:
                update_expression += ", executed_quantity = :executed_quantity"
                expression_values[':executed_quantity'] = str(updates.executed_quantity)

            # Add executed price update if provided
            if updates.executed_price is not None:
                update_expression += ", executed_price = :executed_price"
                expression_values[':executed_price'] = str(updates.executed_price)

            # Add completed_at update if provided
            if updates.completed_at is not None:
                update_expression += ", completed_at = :completed_at"
                expression_values[':completed_at'] = updates.completed_at.isoformat()

            # Update GSI2-SK if status changed
            if updates.status is not None:
                new_gsi2_sk = f"{existing_order.asset_id}#{updates.status.value}#{existing_order.created_at.isoformat()}"
                update_expression += ", GSI2-SK = :gsi2_sk"
                expression_values[':gsi2_sk'] = new_gsi2_sk

            # Perform update
            response = self.db.orders_table.update_item(
                Key={'order_id': order_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values,
                ReturnValues='ALL_NEW'
            )

            updated_item = response['Attributes']
            return Order(**updated_item)

        except EntityNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to update order {order_id}: {str(e)}")
            raise DatabaseOperationError(f"Failed to update order: {str(e)}")

    def get_orders_by_user(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Order]:
        """
        Get all orders for a user.

        Args:
            user_id: User ID to get orders for
            limit: Maximum number of orders to return
            offset: Number of orders to skip

        Returns:
            List of orders

        Raises:
            DatabaseOperationError: If database operation fails
        """
        try:
            response = self.db.orders_table.query(
                IndexName='GSI2',
                KeyConditionExpression=Key('GSI2-PK').eq(user_id),
                Limit=limit,
                ScanIndexForward=False  # Most recent first
            )

            orders = [Order(**item) for item in response.get('Items', [])]

            # Apply offset (DynamoDB doesn't support offset directly)
            if offset > 0:
                orders = orders[offset:]

            return orders

        except Exception as e:
            logger.error(f"Failed to get orders for user {user_id}: {str(e)}")
            raise DatabaseOperationError(f"Failed to get orders for user: {str(e)}")

    def get_orders_by_user_and_asset(self, user_id: str, asset_id: str, limit: int = 50, offset: int = 0) -> List[Order]:
        """
        Get user's orders for specific asset.

        Args:
            user_id: User ID to get orders for
            asset_id: Asset ID to filter by
            limit: Maximum number of orders to return
            offset: Number of orders to skip

        Returns:
            List of orders

        Raises:
            DatabaseOperationError: If database operation fails
        """
        try:
            asset_prefix = f"{asset_id}#"

            response = self.db.orders_table.query(
                IndexName='GSI2',
                KeyConditionExpression=Key('GSI2-PK').eq(user_id) & Key('GSI2-SK').begins_with(asset_prefix),
                Limit=limit,
                ScanIndexForward=False  # Most recent first
            )

            orders = [Order(**item) for item in response.get('Items', [])]

            # Apply offset
            if offset > 0:
                orders = orders[offset:]

            return orders

        except Exception as e:
            logger.error(f"Failed to get orders for user {user_id} and asset {asset_id}: {str(e)}")
            raise DatabaseOperationError(f"Failed to get orders for user and asset: {str(e)}")

    def get_orders_by_user_and_status(self, user_id: str, status: OrderStatus, limit: int = 50, offset: int = 0) -> List[Order]:
        """
        Get user's orders by status.

        Args:
            user_id: User ID to get orders for
            status: Order status to filter by
            limit: Maximum number of orders to return
            offset: Number of orders to skip

        Returns:
            List of orders

        Raises:
            DatabaseOperationError: If database operation fails
        """
        try:
            # Query all user orders and filter by status
            all_orders = self.get_orders_by_user(user_id, limit=1000)  # Get more to filter
            filtered_orders = [order for order in all_orders if order.status == status]

            # Apply limit and offset
            if offset > 0:
                filtered_orders = filtered_orders[offset:]

            return filtered_orders[:limit]

        except Exception as e:
            logger.error(f"Failed to get orders for user {user_id} with status {status}: {str(e)}")
            raise DatabaseOperationError(f"Failed to get orders for user and status: {str(e)}")

    def update_order_status(self, order_id: str, new_status: OrderStatus, reason: str = None) -> Optional[Order]:
        """
        Update order status with validation.

        Args:
            order_id: Order ID to update
            new_status: New status to set
            reason: Optional reason for status change

        Returns:
            Updated order if successful, None if not found

        Raises:
            EntityNotFoundError: If order not found
            BusinessRuleError: If invalid status transition
            DatabaseOperationError: If database operation fails
        """
        try:
            # Get existing order
            existing_order = self.get_order(order_id)
            if not existing_order:
                raise EntityNotFoundError(f"Order {order_id} not found")

            # Validate status transition
            can_transition, error_msg = existing_order.can_transition_to(new_status)
            if not can_transition:
                raise BusinessRuleError(f"Invalid status transition: {error_msg}")

            # Create update object
            updates = OrderUpdate(status=new_status)

            # Add completion timestamp if transitioning to completed
            if new_status == OrderStatus.COMPLETED:
                updates.completed_at = datetime.now(timezone.utc)

            # Update the order
            return self.update_order(order_id, updates)

        except (EntityNotFoundError, BusinessRuleError):
            raise
        except Exception as e:
            logger.error(f"Failed to update order status {order_id} to {new_status}: {str(e)}")
            raise DatabaseOperationError(f"Failed to update order status: {str(e)}")

    def order_exists(self, order_id: str) -> bool:
        """
        Check if order exists.

        Args:
            order_id: Order ID to check

        Returns:
            True if order exists, False otherwise

        Raises:
            DatabaseOperationError: If database operation fails
        """
        try:
            response = self.db.orders_table.get_item(
                Key={'order_id': order_id},
                ProjectionExpression='order_id'
            )

            return 'Item' in response

        except Exception as e:
            logger.error(f"Failed to check if order {order_id} exists: {str(e)}")
            raise DatabaseOperationError(f"Failed to check order existence: {str(e)}")

    # Future implementation methods (commented out for now)
    # def get_orders_by_status(self, status: OrderStatus, limit: int = 50) -> List[Order]:
    #     """Get orders by status (admin functionality) - TODO: Add later"""
    #     pass
    #
    # def get_order_count_by_user(self, user_id: str) -> int:
    #     """Count user's total orders - TODO: Add for analytics/metrics"""
    #     pass
    #
    # def get_order_count_by_status(self, status: OrderStatus) -> int:
    #     """Count orders by status - TODO: Add for analytics/metrics"""
    #     pass
    #
    # def get_total_value_by_asset(self, user_id: str, asset_id: str) -> Decimal:
    #     """Get total completed value for specific asset - TODO: Add later"""
    #     pass
    #
    # def get_total_value_by_user(self, user_id: str) -> Decimal:
    #     """Get total completed value for user - TODO: Add later"""
    #     pass