# services/common/database/dynamodb_service.py
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
import uuid

from .dynamodb_connection import DynamoDBConnection
from ..models.order import Order, OrderCreate, OrderItem, OrderStatus
from ..models.inventory import InventoryItem, InventoryUpdate


class OrderService:
    """Service layer for order operations using DynamoDB"""

    def __init__(self, db_connection: DynamoDBConnection):
        self.db = db_connection

    async def create_order(self, order_create: OrderCreate) -> Order:
        """Create a new order with items"""
        # Generate unique order ID
        order_id = str(uuid.uuid4())
        customer_id = str(uuid.uuid4())  # In real app, get from auth

        now = datetime.utcnow()

        # Calculate total (you'd get prices from product service)
        total_amount = Decimal('0.00')
        for item in order_create.items:
            # Mock price lookup - in real app, fetch from product service
            mock_price = Decimal('29.99')  # Replace with actual price lookup
            total_amount += mock_price * item.quantity

        # Create order data
        order_data = {
            'order_id': order_id,
            'customer_id': customer_id,
            'customer_email': str(order_create.customer_email),
            'customer_name': order_create.customer_name,
            'status': OrderStatus.PENDING.value,
            'total_amount': total_amount,
            'currency': 'USD',
            'shipping_address': order_create.shipping_address,
            'created_at': now,
            'updated_at': now
        }

        # Create order in DynamoDB
        await self.db.create_order(order_data)

        # Create order items
        for item_create in order_create.items:
            mock_price = Decimal('29.99')  # Replace with actual price lookup
            line_total = mock_price * item_create.quantity

            item_data = {
                'product_id': item_create.product_id,
                'quantity': item_create.quantity,
                'unit_price': mock_price,
                'line_total': line_total
            }

            await self.db.create_order_item(order_id, item_data)

        # Return created order
        return Order(
            order_id=order_id,
            customer_id=customer_id,
            customer_email=str(order_create.customer_email),
            customer_name=order_create.customer_name,
            status=OrderStatus.PENDING,
            total_amount=total_amount,
            currency='USD',
            shipping_address=order_create.shipping_address,
            created_at=now,
            updated_at=now
        )

    async def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID"""
        order_data = await self.db.get_order(order_id)

        if not order_data:
            return None

        # Convert DynamoDB item to Order model
        return Order(
            order_id=order_data['order_id'],
            customer_id=order_data['customer_id'],
            customer_email=order_data['customer_email'],
            customer_name=order_data['customer_name'],
            status=OrderStatus(order_data['status']),
            total_amount=Decimal(order_data['total_amount']),
            currency=order_data.get('currency', 'USD'),
            shipping_address=order_data.get('shipping_address'),
            created_at=datetime.fromisoformat(order_data['created_at']),
            updated_at=datetime.fromisoformat(order_data['updated_at'])
        )

    async def get_order_with_items(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get order with its items"""
        order = await self.get_order(order_id)
        if not order:
            return None

        # Get order items
        items_data = await self.db.get_order_items(order_id)

        # Convert to OrderItem models
        items = []
        for item_data in items_data:
            item = OrderItem(
                product_id=item_data['product_id'],
                product_name=f"Product {item_data['product_id'][:8]}",  # Mock name
                quantity=item_data['quantity'],
                unit_price=Decimal(item_data['unit_price']),
                line_total=Decimal(item_data['line_total'])
            )
            items.append(item)

        return {
            'order': order,
            'items': items
        }

    async def update_order_status(self, order_id: str, status: OrderStatus) -> Optional[Order]:
        """Update order status"""
        updated_at = datetime.utcnow().isoformat()

        result = await self.db.update_order_status(order_id, status.value, updated_at)

        if not result:
            return None

        # Convert updated data to Order model
        return Order(
            order_id=result['order_id'],
            customer_id=result['customer_id'],
            customer_email=result['customer_email'],
            customer_name=result['customer_name'],
            status=OrderStatus(result['status']),
            total_amount=Decimal(result['total_amount']),
            currency=result.get('currency', 'USD'),
            shipping_address=result.get('shipping_address'),
            created_at=datetime.fromisoformat(result['created_at']),
            updated_at=datetime.fromisoformat(result['updated_at'])
        )

    async def list_customer_orders(self, customer_id: str) -> List[Order]:
        """List orders for a customer"""
        orders_data = await self.db.list_orders_by_customer(customer_id)

        orders = []
        for order_data in orders_data:
            order = Order(
                order_id=order_data['order_id'],
                customer_id=order_data['customer_id'],
                customer_email=order_data['customer_email'],
                customer_name=order_data['customer_name'],
                status=OrderStatus(order_data['status']),
                total_amount=Decimal(order_data['total_amount']),
                currency=order_data.get('currency', 'USD'),
                shipping_address=order_data.get('shipping_address'),
                created_at=datetime.fromisoformat(order_data['created_at']),
                updated_at=datetime.fromisoformat(order_data['updated_at'])
            )
            orders.append(order)

        return orders


class InventoryService:
    """Service layer for inventory operations using DynamoDB"""

    def __init__(self, db_connection: DynamoDBConnection):
        self.db = db_connection

    async def get_inventory(self, product_id: str) -> Optional[InventoryItem]:
        """Get inventory for a product"""
        inventory_data = await self.db.get_inventory(product_id)

        if not inventory_data:
            return None

        return InventoryItem(
            product_id=inventory_data['product_id'],
            stock_quantity=inventory_data['stock_quantity'],
            reserved_quantity=inventory_data['reserved_quantity'],
            min_stock_level=inventory_data.get('min_stock_level', 10),
            warehouse_location=inventory_data.get('warehouse_location'),
            last_restocked_at=datetime.fromisoformat(inventory_data['last_restocked_at']) if inventory_data.get('last_restocked_at') else None,
            created_at=datetime.fromisoformat(inventory_data['created_at']),
            updated_at=datetime.fromisoformat(inventory_data['updated_at'])
        )

    async def update_inventory(self, product_id: str, inventory_update: InventoryUpdate) -> Optional[InventoryItem]:
        """Update inventory stock"""
        updated_at = datetime.utcnow().isoformat()

        result = await self.db.update_inventory(product_id, inventory_update.quantity_change, updated_at)

        if not result:
            return None

        return InventoryItem(
            product_id=result['product_id'],
            stock_quantity=result['stock_quantity'],
            reserved_quantity=result['reserved_quantity'],
            min_stock_level=result.get('min_stock_level', 10),
            warehouse_location=result.get('warehouse_location'),
            last_restocked_at=datetime.fromisoformat(result['last_restocked_at']) if result.get('last_restocked_at') else None,
            created_at=datetime.fromisoformat(result['created_at']),
            updated_at=datetime.fromisoformat(result['updated_at'])
        )

    async def reserve_stock(self, product_id: str, quantity: int) -> bool:
        """Reserve stock for an order"""
        try:
            updated_at = datetime.utcnow().isoformat()
            await self.db.reserve_stock(product_id, quantity, updated_at)
            return True
        except Exception:
            return False

    async def check_stock_availability(self, product_id: str, requested_quantity: int) -> bool:
        """Check if enough stock is available"""
        inventory = await self.get_inventory(product_id)

        if not inventory:
            return False

        return inventory.available_quantity >= requested_quantity