"""
Order DAO for database operations.
Handles CRUD operations for Order entities using DynamoDB.
"""

from typing import List
from datetime import datetime, timezone

from boto3.dynamodb.conditions import Key, Attr

from ..base_dao import BaseDAO
from ...entities.order import Order, OrderItem
from ...entities.order.enums import OrderStatus
from ...exceptions import CNOPDatabaseOperationException
from ....exceptions.shared_exceptions import CNOPOrderNotFoundException
from ....exceptions import CNOPEntityValidationException
from ....shared.logging import BaseLogger, Loggers, LogActions

logger = BaseLogger(Loggers.DATABASE, log_to_file=True)


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
            CNOPDatabaseOperationException: If database operation fails
        """
        try:
            # Convert Order entity to OrderItem for database storage
            order_item = OrderItem.from_entity(order)
            item = order_item.model_dump()

            # Add GSI attributes for UserOrdersIndex
            item['GSI-PK'] = order.username
            item['GSI-SK'] = order.asset_id

            # Insert into DynamoDB
            logger.info(
                action=LogActions.DB_OPERATION,
                message=f"Order item prepared: {item}"
            )
            self.table.put_item(Item=item)

            logger.info(
                action=LogActions.DB_OPERATION,
                message=f"Order created successfully: id={order.order_id}, user={order.username}, "
                       f"asset={order.asset_id}, type={order.order_type.value}"
            )
            return order

        except Exception as e:
            logger.error(
                action=LogActions.ERROR,
                message=f"Failed to create order '{order.order_id}': {str(e)}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while creating order '{order.order_id}': {str(e)}")

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
        key = {'Pk': order_id, 'Sk': 'ORDER'}
        item = self._safe_get_item(self.table, key)

        if not item:
            raise CNOPOrderNotFoundException(f"Order '{order_id}' not found")

        # Convert database item to OrderItem and then to Order entity
        order_item = OrderItem(**item)
        return order_item.to_entity()


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
            response = self.table.query(
                IndexName='UserOrdersIndex',
                KeyConditionExpression=Key('GSI-PK').eq(username),
                Limit=limit,
                ScanIndexForward=False  # Most recent first
            )

            # Convert each item to OrderItem and then to Order entity
            orders = []
            for item in response.get('Items', []):
                order_item = OrderItem(**item)
                orders.append(order_item.to_entity())

            # Apply offset (DynamoDB doesn't support offset directly)
            if offset > 0:
                orders = orders[offset:]

            return orders

        except Exception as e:
            logger.error(
            action=LogActions.ERROR,
            message=f"Failed to get orders for user '{username}': {str(e)}"
        )
            raise CNOPDatabaseOperationException(f"Database operation failed while retrieving orders for user '{username}': {str(e)}")


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

            logger.info(
                action=LogActions.DB_OPERATION,
                message=f"Order status updated successfully: id={order_id}, new_status={new_status.value}, reason={reason or 'none'}"
            )

            # Convert database item to OrderItem and then to Order entity
            order_item = OrderItem(**updated_item)
            return order_item.to_entity()

        except Exception as e:
            logger.error(
                action=LogActions.ERROR,
                message=f"Failed to update order status '{order_id}': {str(e)}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while updating order status for order '{order_id}': {str(e)}")

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
            response = self.table.get_item(
                Key={'Pk': order_id, 'Sk': 'ORDER'},
                ProjectionExpression='order_id'
            )

            return 'Item' in response

        except Exception as e:
            logger.error(
                action=LogActions.ERROR,
                message=f"Failed to check if order '{order_id}' exists: {str(e)}"
            )
            raise CNOPDatabaseOperationException(f"Database operation failed while checking existence of order '{order_id}': {str(e)}")
