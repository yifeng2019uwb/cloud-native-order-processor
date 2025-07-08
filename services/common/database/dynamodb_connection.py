# services/common/database/dynamodb_connection.py
import os
import boto3
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, Any, Optional
import logging
from boto3.dynamodb.conditions import Key, Attr

logger = logging.getLogger(__name__)


class DynamoDBManager:
    def __init__(self):
        # Get table names from environment variables (set by Terraform)
        self.orders_table_name = os.getenv("ORDERS_TABLE")
        self.inventory_table_name = os.getenv("INVENTORY_TABLE")

        if not self.orders_table_name or not self.inventory_table_name:
            raise ValueError("DynamoDB table names not found in environment variables")

        # Initialize boto3 client and resource
        self.region = os.getenv("REGION", "us-west-2")  # Note: not AWS_REGION
        self.dynamodb = boto3.resource('dynamodb', region_name=self.region)
        self.client = boto3.client('dynamodb', region_name=self.region)

        # Get table references
        self.orders_table = self.dynamodb.Table(self.orders_table_name)
        self.inventory_table = self.dynamodb.Table(self.inventory_table_name)

        logger.info(f"DynamoDB initialized - Orders: {self.orders_table_name}, Inventory: {self.inventory_table_name}")

    async def health_check(self) -> bool:
        """Check if DynamoDB tables are accessible"""
        try:
            # Test connection by describing tables
            self.orders_table.meta.client.describe_table(TableName=self.orders_table_name)
            self.inventory_table.meta.client.describe_table(TableName=self.inventory_table_name)
            return True
        except Exception as e:
            logger.error(f"DynamoDB health check failed: {e}")
            return False

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator['DynamoDBConnection', None]:
        """Get DynamoDB connection wrapper"""
        connection = DynamoDBConnection(self.orders_table, self.inventory_table)
        try:
            yield connection
        finally:
            # DynamoDB doesn't need explicit connection cleanup
            pass


class DynamoDBConnection:
    """DynamoDB connection wrapper that mimics asyncpg interface"""

    def __init__(self, orders_table, inventory_table):
        self.orders_table = orders_table
        self.inventory_table = inventory_table

    # Orders operations
    async def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an order in DynamoDB"""
        try:
            # DynamoDB single-table design
            item = {
                'PK': f"ORDER#{order_data['order_id']}",
                'SK': 'METADATA',
                'order_id': order_data['order_id'],
                'customer_id': order_data['customer_id'],
                'customer_email': order_data['customer_email'],
                'customer_name': order_data['customer_name'],
                'status': order_data['status'],
                'total_amount': str(order_data['total_amount']),  # Store as string for precision
                'currency': order_data.get('currency', 'USD'),
                'shipping_address': order_data.get('shipping_address'),
                'created_at': order_data['created_at'].isoformat(),
                'updated_at': order_data['updated_at'].isoformat(),
                'entity_type': 'ORDER'
            }

            response = self.orders_table.put_item(Item=item)
            return item
        except Exception as e:
            logger.error(f"Failed to create order: {e}")
            raise

    async def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get an order by ID"""
        try:
            response = self.orders_table.get_item(
                Key={
                    'PK': f"ORDER#{order_id}",
                    'SK': 'METADATA'
                }
            )
            return response.get('Item')
        except Exception as e:
            logger.error(f"Failed to get order {order_id}: {e}")
            raise

    async def update_order_status(self, order_id: str, status: str, updated_at: str):
        """Update order status"""
        try:
            response = self.orders_table.update_item(
                Key={
                    'PK': f"ORDER#{order_id}",
                    'SK': 'METADATA'
                },
                UpdateExpression='SET #status = :status, updated_at = :updated_at',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':status': status,
                    ':updated_at': updated_at
                },
                ReturnValues='ALL_NEW'
            )
            return response.get('Attributes')
        except Exception as e:
            logger.error(f"Failed to update order status: {e}")
            raise

    async def list_orders_by_customer(self, customer_id: str) -> list:
        """List orders by customer using GSI"""
        try:
            response = self.orders_table.query(
                IndexName='CustomerIndex',
                KeyConditionExpression=Key('customer_id').eq(customer_id)
            )
            return response.get('Items', [])
        except Exception as e:
            logger.error(f"Failed to list orders for customer {customer_id}: {e}")
            raise

    # Order Items operations
    async def create_order_item(self, order_id: str, item_data: Dict[str, Any]):
        """Create an order item"""
        try:
            item = {
                'PK': f"ORDER#{order_id}",
                'SK': f"ITEM#{item_data['product_id']}",
                'order_id': order_id,
                'product_id': item_data['product_id'],
                'quantity': item_data['quantity'],
                'unit_price': str(item_data['unit_price']),
                'line_total': str(item_data['line_total']),
                'entity_type': 'ORDER_ITEM'
            }

            response = self.orders_table.put_item(Item=item)
            return item
        except Exception as e:
            logger.error(f"Failed to create order item: {e}")
            raise

    async def get_order_items(self, order_id: str) -> list:
        """Get all items for an order"""
        try:
            response = self.orders_table.query(
                KeyConditionExpression=Key('PK').eq(f"ORDER#{order_id}") & Key('SK').begins_with('ITEM#')
            )
            return response.get('Items', [])
        except Exception as e:
            logger.error(f"Failed to get order items for {order_id}: {e}")
            raise

    # Inventory operations
    async def get_inventory(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get inventory for a product"""
        try:
            response = self.inventory_table.get_item(
                Key={'product_id': product_id}
            )
            return response.get('Item')
        except Exception as e:
            logger.error(f"Failed to get inventory for {product_id}: {e}")
            raise

    async def update_inventory(self, product_id: str, stock_change: int, updated_at: str):
        """Update inventory stock"""
        try:
            response = self.inventory_table.update_item(
                Key={'product_id': product_id},
                UpdateExpression='SET stock_quantity = stock_quantity + :change, updated_at = :updated_at',
                ExpressionAttributeValues={
                    ':change': stock_change,
                    ':updated_at': updated_at
                },
                ReturnValues='ALL_NEW'
            )
            return response.get('Attributes')
        except Exception as e:
            logger.error(f"Failed to update inventory for {product_id}: {e}")
            raise

    async def reserve_stock(self, product_id: str, quantity: int, updated_at: str):
        """Reserve stock for an order"""
        try:
            response = self.inventory_table.update_item(
                Key={'product_id': product_id},
                UpdateExpression='SET reserved_quantity = reserved_quantity + :qty, updated_at = :updated_at',
                ExpressionAttributeValues={
                    ':qty': quantity,
                    ':updated_at': updated_at
                },
                ReturnValues='ALL_NEW'
            )
            return response.get('Attributes')
        except Exception as e:
            logger.error(f"Failed to reserve stock for {product_id}: {e}")
            raise


# Global DynamoDB manager instance (replaces PostgreSQL db_manager)
dynamodb_manager = DynamoDBManager()


# Updated dependency for FastAPI (replaces get_db)
async def get_dynamodb():
    async with dynamodb_manager.get_connection() as conn:
        yield conn