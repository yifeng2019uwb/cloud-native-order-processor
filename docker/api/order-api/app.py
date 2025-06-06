import json
from typing import List, Dict, Optional

from models import Order, PaymentTransaction


class OrderProcessor:
    def __init__(self, db_manager):
        self.db = db_manager

    def create_order(self, order: Order) -> bool:
        """Create a new order with inventory validation and reservation"""
        try:
            # First, check and reserve inventory for all items
            reservations_made = []

            for item in order.items:
                # Check if we have enough stock
                available = self._check_available_stock(item["product_id"])
                if available < item["quantity"]:
                    # Rollback any reservations made
                    self._rollback_reservations(reservations_made)
                    raise ValueError(
                        f"Insufficient stock for product {item['product_id']}"
                    )

                # Reserve the stock
                success = self.db.reserve_stock(item["product_id"], item["quantity"])
                if not success:
                    # Rollback any reservations made
                    self._rollback_reservations(reservations_made)
                    raise ValueError(
                        f"Failed to reserve stock for product {item['product_id']}"
                    )

                reservations_made.append(
                    {"product_id": item["product_id"], "quantity": item["quantity"]}
                )

            # Create the order in database
            success = self.db.create_order(order)
            if not success:
                # Rollback reservations if order creation failed
                self._rollback_reservations(reservations_made)
                return False

            return True

        except Exception as e:
            print(f"Error creating order: {str(e)}")
            return False

    def get_order(self, order_id: str) -> Optional[Dict]:
        """Get order details by ID"""
        try:
            return self.db.get_order(order_id)
        except Exception as e:
            print(f"Error getting order {order_id}: {str(e)}")
            return None

    def list_orders(
        self, limit: int = 50, status: str = None, customer_email: str = None
    ) -> List[Dict]:
        """List orders with optional filtering"""
        try:
            orders = self.db.list_orders(limit)

            # Apply filters if provided
            if status:
                orders = [order for order in orders if order["status"] == status]

            if customer_email:
                orders = [
                    order
                    for order in orders
                    if order["customer_email"] == customer_email
                ]

            return orders
        except Exception as e:
            print(f"Error listing orders: {str(e)}")
            return []

    def update_order_status(self, order_id: str, new_status: str) -> bool:
        """Update order status with validation"""
        try:
            # Validate status transition
            current_order = self.get_order(order_id)
            if not current_order:
                return False

            current_status = current_order["status"]

            # Define valid status transitions
            valid_transitions = {
                "pending": ["confirmed", "cancelled"],
                "confirmed": ["processing", "cancelled"],
                "processing": ["shipped", "cancelled"],
                "shipped": ["delivered"],
                "paid": ["processing", "refunded"],
                "delivered": [],
                "cancelled": [],
                "refunded": [],
            }

            if new_status not in valid_transitions.get(current_status, []):
                print(
                    f"Invalid status transition from {current_status} to {new_status}"
                )
                return False

            # Handle special status changes
            if new_status == "cancelled":
                self._handle_order_cancellation(order_id)
            elif new_status == "delivered":
                self._handle_order_delivery(order_id)

            return self.db.update_order_status(order_id, new_status)

        except Exception as e:
            print(f"Error updating order status: {str(e)}")
            return False

    def process_payment(self, transaction: PaymentTransaction) -> bool:
        """Process payment transaction"""
        try:
            # In a real implementation, this would integrate with payment gateways
            # For now, we'll simulate payment processing

            # Validate order exists and is payable
            order = self.get_order(transaction.order_id)
            if not order:
                return False

            if order["status"] not in ["pending", "confirmed"]:
                print(f"Order {transaction.order_id} is not in a payable state")
                return False

            # Validate payment amount
            if float(transaction.amount) != float(order["total_amount"]):
                print("Payment amount does not match order total")
                return False

            # Save payment transaction
            success = self._save_payment_transaction(transaction)
            if success:
                # Update order status to paid
                self.update_order_status(transaction.order_id, "paid")
                return True

            return False

        except Exception as e:
            print(f"Error processing payment: {str(e)}")
            return False

    def calculate_order_total(self, items: List[Dict]) -> float:
        """Calculate total amount for order items"""
        total = 0.0
        for item in items:
            # Get current product price
            product = self.db.get_product(item["product_id"])
            if product:
                total += float(product["price"]) * item["quantity"]
        return total

    def get_order_analytics(self, start_date: str = None, end_date: str = None) -> Dict:
        """Get order analytics and statistics"""
        try:
            orders = self.list_orders(limit=1000)  # Get more orders for analytics

            # Filter by date range if provided
            if start_date or end_date:
                filtered_orders = []
                for order in orders:
                    order_date = order["created_at"]
                    if start_date and order_date < start_date:
                        continue
                    if end_date and order_date > end_date:
                        continue
                    filtered_orders.append(order)
                orders = filtered_orders

            # Calculate analytics
            total_orders = len(orders)
            total_revenue = sum(float(order["total_amount"]) for order in orders)
            average_order_value = (
                total_revenue / total_orders if total_orders > 0 else 0
            )

            # Status breakdown
            status_counts = {}
            for order in orders:
                status = order["status"]
                status_counts[status] = status_counts.get(status, 0) + 1

            # Top customers
            customer_orders = {}
            for order in orders:
                email = order["customer_email"]
                if email not in customer_orders:
                    customer_orders[email] = {"count": 0, "total_spent": 0}
                customer_orders[email]["count"] += 1
                customer_orders[email]["total_spent"] += float(order["total_amount"])

            top_customers = sorted(
                customer_orders.items(), key=lambda x: x[1]["total_spent"], reverse=True
            )[:10]

            return {
                "total_orders": total_orders,
                "total_revenue": total_revenue,
                "average_order_value": average_order_value,
                "status_breakdown": status_counts,
                "top_customers": [
                    {
                        "email": email,
                        "order_count": data["count"],
                        "total_spent": data["total_spent"],
                    }
                    for email, data in top_customers
                ],
            }

        except Exception as e:
            print(f"Error getting order analytics: {str(e)}")
            return {}

    def _check_available_stock(self, product_id: str) -> int:
        """Check available stock for a product"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT stock_quantity, reserved_quantity 
                    FROM inventory 
                    WHERE product_id = %s
                """,
                    (product_id,),
                )

                result = cursor.fetchone()
                if result:
                    stock_quantity, reserved_quantity = result
                    return stock_quantity - reserved_quantity
                return 0
        except Exception as e:
            print(f"Error checking stock for {product_id}: {str(e)}")
            return 0

    def _rollback_reservations(self, reservations: List[Dict]):
        """Rollback stock reservations"""
        for reservation in reservations:
            try:
                with self.db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        UPDATE inventory 
                        SET reserved_quantity = reserved_quantity - %s
                        WHERE product_id = %s
                    """,
                        (reservation["quantity"], reservation["product_id"]),
                    )
                    conn.commit()
            except Exception as e:
                print(f"Error rolling back reservation: {str(e)}")

    def _handle_order_cancellation(self, order_id: str):
        """Handle order cancellation - release reserved stock"""
        try:
            order = self.get_order(order_id)
            if order and order["items"]:
                for item in order["items"]:
                    # Release reserved stock
                    with self.db.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            """
                            UPDATE inventory 
                            SET reserved_quantity = reserved_quantity - %s
                            WHERE product_id = %s
                        """,
                            (item["quantity"], item["product_id"]),
                        )
                        conn.commit()
        except Exception as e:
            print(f"Error handling order cancellation: {str(e)}")

    def _handle_order_delivery(self, order_id: str):
        """Handle order delivery - convert reserved stock to sold"""
        try:
            order = self.get_order(order_id)
            if order and order["items"]:
                for item in order["items"]:
                    # Reduce stock and reserved quantities
                    with self.db.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            """
                            UPDATE inventory 
                            SET stock_quantity = stock_quantity - %s,
                                reserved_quantity = reserved_quantity - %s
                            WHERE product_id = %s
                        """,
                            (item["quantity"], item["quantity"], item["product_id"]),
                        )
                        conn.commit()
        except Exception as e:
            print(f"Error handling order delivery: {str(e)}")

    def _save_payment_transaction(self, transaction: PaymentTransaction) -> bool:
        """Save payment transaction to database"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO payment_transactions 
                    (transaction_id, order_id, amount, status, payment_method, gateway_response, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                    (
                        transaction.transaction_id,
                        transaction.order_id,
                        transaction.amount,
                        transaction.status,
                        transaction.payment_method,
                        json.dumps(transaction.gateway_response),
                        transaction.created_at,
                    ),
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error saving payment transaction: {str(e)}")
            return False
