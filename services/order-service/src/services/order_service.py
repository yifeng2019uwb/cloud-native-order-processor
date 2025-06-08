import sys
import os
import json
import uuid
from datetime import datetime
from typing import List, Optional
from decimal import Decimal
import asyncpg

from models.order import OrderCreate, OrderResponse, OrderItem, OrderStatus
from database.queries import OrderQueries, ProductQueries, InventoryQueries
from .event_service import EventService

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "common"))


class OrderService:
    def __init__(self):
        self.event_service = EventService()

    async def create_order(
        self, order_data: OrderCreate, db: asyncpg.Connection
    ) -> OrderResponse:
        """Create a new order with inventory validation"""

        # Generate order ID
        order_id = str(uuid.uuid4())
        customer_id = str(uuid.uuid4())  # In real app, get from auth

        # Validate and calculate order
        order_items = []
        total_amount = Decimal("0.00")

        for item in order_data.items:
            # Get product details
            product = await db.fetchrow(ProductQueries.GET_PRODUCT, item.product_id)

            if not product:
                raise ValueError(f"Product {item.product_id} not found")

            # Check inventory
            inventory = await db.fetchrow(
                InventoryQueries.GET_INVENTORY, item.product_id
            )

            if not inventory:
                raise ValueError(f"No inventory found for product {item.product_id}")

            available = inventory["stock_quantity"] - inventory["reserved_quantity"]
            if available < item.quantity:
                raise ValueError(
                    f"Insufficient stock for {product['name']}. Available: {available}"
                )

            # Calculate line total
            line_total = Decimal(str(product["price"])) * item.quantity
            total_amount += line_total

            order_items.append(
                OrderItem(
                    product_id=item.product_id,
                    product_name=product["name"],
                    quantity=item.quantity,
                    unit_price=Decimal(str(product["price"])),
                    line_total=line_total,
                )
            )

        # Start transaction
        async with db.transaction():
            # Create order
            await db.execute(
                OrderQueries.CREATE_ORDER,
                order_id,
                customer_id,
                order_data.customer_email,
                order_data.customer_name,
                OrderStatus.PENDING,
                total_amount,
                (
                    json.dumps(order_data.shipping_address)
                    if order_data.shipping_address
                    else None
                ),
                datetime.utcnow(),
            )

            # Create order items and reserve inventory
            for item in order_items:
                # Insert order item
                await db.execute(
                    OrderQueries.CREATE_ORDER_ITEM,
                    order_id,
                    item.product_id,
                    item.quantity,
                    item.unit_price,
                    item.line_total,
                )

                # Reserve inventory
                await db.execute(
                    InventoryQueries.RESERVE_STOCK,
                    item.quantity,
                    datetime.utcnow(),
                    item.product_id,
                )

        # Create response
        order_response = OrderResponse(
            order_id=order_id,
            customer_email=order_data.customer_email,
            customer_name=order_data.customer_name,
            status=OrderStatus.PENDING,
            total_amount=total_amount,
            currency="USD",
            items=order_items,
            shipping_address=order_data.shipping_address,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Publish event
        await self.event_service.publish_order_event("order_created", order_response)

        return order_response

    async def get_order(
        self, order_id: str, db: asyncpg.Connection
    ) -> Optional[OrderResponse]:
        """Get order by ID"""
        order = await db.fetchrow(OrderQueries.GET_ORDER, order_id)

        if not order:
            return None

        # Get order items
        items = await db.fetch(OrderQueries.GET_ORDER_ITEMS, order_id)

        order_items = [
            OrderItem(
                product_id=item["product_id"],
                product_name=item["product_name"],
                quantity=item["quantity"],
                unit_price=Decimal(str(item["unit_price"])),
                line_total=Decimal(str(item["line_total"])),
            )
            for item in items
        ]

        shipping_address = None
        if order["shipping_address"]:
            shipping_address = json.loads(order["shipping_address"])

        return OrderResponse(
            order_id=order["order_id"],
            customer_email=order["customer_email"],
            customer_name=order.get("customer_name", "Unknown"),
            status=OrderStatus(order["status"]),
            total_amount=Decimal(str(order["total_amount"])),
            currency=order.get("currency", "USD"),
            items=order_items,
            shipping_address=shipping_address,
            created_at=order["created_at"],
            updated_at=order["updated_at"],
        )

    async def list_orders(
        self,
        db: asyncpg.Connection,
        limit: int = 50,
        status: Optional[str] = None,
        customer_email: Optional[str] = None,
    ) -> List[OrderResponse]:
        """List orders with optional filtering"""
        query = OrderQueries.LIST_ORDERS
        params = []
        param_count = 0

        if status:
            param_count += 1
            query += f" AND status = ${param_count}"
            params.append(status)

        if customer_email:
            param_count += 1
            query += f" AND customer_email = ${param_count}"
            params.append(customer_email)

        param_count += 1
        query += f" ORDER BY created_at DESC LIMIT ${param_count}"
        params.append(limit)

        orders = await db.fetch(query, *params)

        result = []
        for order in orders:
            order_response = await self.get_order(order["order_id"], db)
            if order_response:
                result.append(order_response)

        return result

    async def update_order_status(
        self, order_id: str, new_status: OrderStatus, db: asyncpg.Connection
    ) -> bool:
        """Update order status"""
        result = await db.execute(
            OrderQueries.UPDATE_ORDER_STATUS,
            new_status.value,
            datetime.utcnow(),
            order_id,
        )

        if result == "UPDATE 1":
            # Get updated order for event
            order = await self.get_order(order_id, db)
            if order:
                await self.event_service.publish_order_event(
                    "order_status_updated", order
                )
            return True

        return False
