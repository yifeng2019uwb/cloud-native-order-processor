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
from ...exceptions import DatabaseOperationException
from ...exceptions.shared_exceptions import OrderNotFoundException
from ...exceptions import OrderValidationException

logger = logging.getLogger(__name__)


class OrderDAO(BaseDAO):
    """Data Access Object for Order entities"""

    def __init__(self, db_connection):
        """Initialize Order DAO with DynamoDB connection"""
        super().__init__(db_connection)
        # Table reference - change here if we need to switch tables
        self.table = self.db.orders_table

    def create_order(self, order: Order) -> Order:
        """
        Create a new order in the database.

        Args:
            order: Order entity to create

        Returns:
            Created order

        Raises:
            DatabaseOperationException: If database operation fails
        """
        try:
            # Prepare item for DynamoDB with proper serialization
            item = order.model_dump()

            # Convert datetime objects to ISO strings for DynamoDB
            if isinstance(item.get('created_at'), datetime):
                item['created_at'] = item['created_at'].isoformat()
            if isinstance(item.get('updated_at'), datetime):
                item['updated_at'] = item['updated_at'].isoformat()

            # Ensure timestamps are set
            now = datetime.now(timezone.utc)
            if not order.created_at:
                item['created_at'] = now.isoformat()
            if not order.updated_at:
                item['updated_at'] = now.isoformat()

            # Add GSI attributes for UserOrdersIndex
            item['GSI-PK'] = order.username
            item['GSI-SK'] = order.asset_id

            # Insert into DynamoDB
            logger.debug(f"Order item prepared: {item}")
            self.table.put_item(Item=item)

            logger.info(f"Order created successfully: id={order.order_id}, user={order.username}, "
                       f"asset={order.asset_id}, type={order.order_type.value}")
            return order

        except Exception as e:
            logger.error(f"Failed to create order '{order.order_id}': {str(e)}")
            raise DatabaseOperationException(f"Database operation failed while creating order '{order.order_id}': {str(e)}")

    def get_order(self, order_id: str) -> Order:
        """
        Get order by ID.

        Args:
            order_id: Order ID to retrieve

        Returns:
            Order entity if found

        Raises:
            OrderNotFoundException: If order not found
            DatabaseOperationException: If database operation fails
        """
        key = {'Pk': order_id, 'Sk': 'ORDER'}
        item = self._safe_get_item(self.table, key)

        if not item:
            raise OrderNotFoundException(f"Order '{order_id}' not found")

        return Order(**item)

    def update_order(self, order_id: str, updates: OrderUpdate) -> Order:
        """
        Update existing order (only status-related fields).

        Args:
            order_id: Order ID to update
            updates: OrderUpdate object with changes

        Returns:
            Updated order if successful

        Raises:
            EntityNotFoundException: If order not found
            DatabaseOperationException: If database operation fails
        """
        try:
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

            # Perform update
            response = self.table.update_item(
                Key={'Pk': order_id, 'Sk': 'ORDER'},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values,
                ReturnValues='ALL_NEW'
            )

            updated_item = response['Attributes']
            return Order(**updated_item)

        except Exception as e:
            logger.error(f"Failed to update order '{order_id}': {str(e)}")
            raise DatabaseOperationException(f"Database operation failed while updating order '{order_id}': {str(e)}")

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
            DatabaseOperationError: If database operation fails
        """
        try:
            response = self.table.query(
                IndexName='UserOrdersIndex',
                KeyConditionExpression=Key('GSI-PK').eq(username),
                Limit=limit,
                ScanIndexForward=False  # Most recent first
            )

            orders = [Order(**item) for item in response.get('Items', [])]

            # Apply offset (DynamoDB doesn't support offset directly)
            if offset > 0:
                orders = orders[offset:]

            return orders

        except Exception as e:
            logger.error(f"Failed to get orders for user '{username}': {str(e)}")
            raise DatabaseOperationException(f"Database operation failed while retrieving orders for user '{username}': {str(e)}")

    def get_orders_by_user_and_asset(self, username: str, asset_id: str, limit: int = 50, offset: int = 0) -> List[Order]:
        """
        Get user's orders for specific asset.

        Args:
            username: Username to get orders for
            asset_id: Asset ID to filter by
            limit: Maximum number of orders to return
            offset: Number of orders to skip

        Returns:
            List of orders

        Raises:
            DatabaseOperationError: If database operation fails
        """
        try:
            response = self.table.query(
                IndexName='UserOrdersIndex',
                KeyConditionExpression=Key('GSI-PK').eq(username) & Key('GSI-SK').eq(asset_id),
                Limit=limit,
                ScanIndexForward=False  # Most recent first
            )

            orders = [Order(**item) for item in response.get('Items', [])]

            # Apply offset
            if offset > 0:
                orders = orders[offset:]

            return orders

        except Exception as e:
            logger.error(f"Failed to get orders for user '{username}' and asset '{asset_id}': {str(e)}")
            raise DatabaseOperationException(f"Database operation failed while retrieving orders for user '{username}' and asset '{asset_id}': {str(e)}")

    def get_orders_by_user_and_status(self, username: str, status: OrderStatus, limit: int = 50, offset: int = 0) -> List[Order]:
        """
        Get user's orders by status.

        Args:
            username: Username to get orders for
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
            all_orders = self.get_orders_by_user(username, limit=1000)  # Get more to filter
            filtered_orders = [order for order in all_orders if order.status == status]

            # Apply limit and offset
            if offset > 0:
                filtered_orders = filtered_orders[offset:]

            return filtered_orders[:limit]

        except Exception as e:
            logger.error(f"Failed to get orders for user '{user_id}' with status '{status.value}': {str(e)}")
            raise DatabaseOperationException(f"Database operation failed while retrieving orders for user '{user_id}' with status '{status.value}': {str(e)}")

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
            EntityNotFoundException: If order not found
            DatabaseOperationException: If database operation fails
        """
        try:
            # Prepare update expression
            update_expression = "SET #status = :status, updated_at = :updated_at"
            expression_values = {
                ':status': new_status.value,
                ':updated_at': datetime.now(timezone.utc).isoformat(),
                '#status': 'status'
            }

            # Add reason if provided
            if reason:
                update_expression += ", status_reason = :reason"
                expression_values[':reason'] = reason

            # Perform update
            response = self.table.update_item(
                Key={'Pk': order_id, 'Sk': 'ORDER'},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values,
                ReturnValues='ALL_NEW'
            )

            updated_item = response['Attributes']
            return Order(**updated_item)

        except Exception as e:
            logger.error(f"Failed to update order status '{order_id}': {str(e)}")
            raise DatabaseOperationException(f"Database operation failed while updating order status for order '{order_id}': {str(e)}")

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
            response = self.table.get_item(
                Key={'Pk': order_id, 'Sk': 'ORDER'},
                ProjectionExpression='order_id'
            )

            return 'Item' in response

        except Exception as e:
            logger.error(f"Failed to check if order '{order_id}' exists: {str(e)}")
            raise DatabaseOperationException(f"Database operation failed while checking existence of order '{order_id}': {str(e)}")
