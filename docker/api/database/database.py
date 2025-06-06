import psycopg2
import psycopg2.extras
import os
import json
from datetime import datetime
from contextmanager import contextmanager
from models import Order, OrderItem, Product

class PostgreSQLManager:
    def __init__(self):
        self.connection_params = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'orderprocessor'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'password')
        }
    
    @contextmanager
    def get_connection(self):
        conn = None
        try:
            conn = psycopg2.connect(**self.connection_params)
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    def create_order(self, order: Order):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                # Insert order
                cursor.execute("""
                    INSERT INTO orders (order_id, customer_email, customer_name, total_amount, status, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    order.order_id, order.customer_email, order.customer_name,
                    order.total_amount, order.status, order.created_at
                ))
                
                # Insert order items
                for item in order.items:
                    cursor.execute("""
                        INSERT INTO order_items (order_id, product_id, product_name, quantity, price)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        order.order_id, item['product_id'], item['product_name'],
                        item['quantity'], item['price']
                    ))
                
                conn.commit()
                return True
            except Exception as e:
                conn.rollback()
                raise e
    
    def get_order(self, order_id: str):
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            # Get order details
            cursor.execute("""
                SELECT * FROM orders WHERE order_id = %s
            """, (order_id,))
            order = cursor.fetchone()
            
            if not order:
                return None
            
            # Get order items
            cursor.execute("""
                SELECT * FROM order_items WHERE order_id = %s
            """, (order_id,))
            items = cursor.fetchall()
            
            order_dict = dict(order)
            order_dict['items'] = [dict(item) for item in items]
            return order_dict
    
    def list_orders(self, limit=50):
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("""
                SELECT o.*, 
                       json_agg(
                           json_build_object(
                               'product_id', oi.product_id,
                               'product_name', oi.product_name,
                               'quantity', oi.quantity,
                               'price', oi.price
                           )
                       ) as items
                FROM orders o
                LEFT JOIN order_items oi ON o.order_id = oi.order_id
                GROUP BY o.order_id, o.customer_email, o.customer_name, o.total_amount, o.status, o.created_at, o.updated_at
                ORDER BY o.created_at DESC
                LIMIT %s
            """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def update_order_status(self, order_id: str, status: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE orders 
                SET status = %s, updated_at = %s 
                WHERE order_id = %s
            """, (status, datetime.utcnow().isoformat(), order_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_products(self, limit=50):
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("""
                SELECT p.*, i.stock_quantity, i.reserved_quantity
                FROM products p
                LEFT JOIN inventory i ON p.product_id = i.product_id
                ORDER BY p.name
                LIMIT %s
            """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_product(self, product_id: str):
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("""
                SELECT p.*, i.stock_quantity, i.reserved_quantity
                FROM products p
                LEFT JOIN inventory i ON p.product_id = i.product_id
                WHERE p.product_id = %s
            """, (product_id,))
            
            result = cursor.fetchone()
            return dict(result) if result else None
    
    def update_stock(self, product_id: str, quantity_change: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE inventory 
                SET stock_quantity = stock_quantity + %s, updated_at = %s
                WHERE product_id = %s
            """, (quantity_change, datetime.utcnow().isoformat(), product_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def reserve_stock(self, product_id: str, quantity: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check available stock
            cursor.execute("""
                SELECT stock_quantity, reserved_quantity 
                FROM inventory 
                WHERE product_id = %s
            """, (product_id,))
            
            result = cursor.fetchone()
            if not result:
                return False
            
            stock_quantity, reserved_quantity = result
            available = stock_quantity - reserved_quantity
            
            if available < quantity:
                return False
            
            # Reserve stock
            cursor.execute("""
                UPDATE inventory 
                SET reserved_quantity = reserved_quantity + %s, updated_at = %s
                WHERE product_id = %s
            """, (quantity, datetime.utcnow().isoformat(), product_id))
            
            conn.commit()
            return True
    
    def initialize_database(self):
        """Create tables if they don't exist"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    product_id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    price DECIMAL(10, 2) NOT NULL,
                    category VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS inventory (
                    product_id VARCHAR(50) PRIMARY KEY REFERENCES products(product_id),
                    stock_quantity INTEGER NOT NULL DEFAULT 0,
                    reserved_quantity INTEGER NOT NULL DEFAULT 0,
                    min_stock_level INTEGER DEFAULT 10,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS orders (
                    order_id VARCHAR(50) PRIMARY KEY,
                    customer_email VARCHAR(255) NOT NULL,
                    customer_name VARCHAR(255) NOT NULL,
                    total_amount DECIMAL(10, 2) NOT NULL,
                    status VARCHAR(50) NOT NULL DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS order_items (
                    id SERIAL PRIMARY KEY,
                    order_id VARCHAR(50) REFERENCES orders(order_id),
                    product_id VARCHAR(50) REFERENCES products(product_id),
                    product_name VARCHAR(255) NOT NULL,
                    quantity INTEGER NOT NULL,
                    price DECIMAL(10, 2) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS payment_transactions (
                    transaction_id VARCHAR(100) PRIMARY KEY,
                    order_id VARCHAR(50) REFERENCES orders(order_id),
                    amount DECIMAL(10, 2) NOT NULL,
                    status VARCHAR(50) NOT NULL,
                    payment_method VARCHAR(50),
                    gateway_response JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Create indexes
                CREATE INDEX IF NOT EXISTS idx_orders_customer_email ON orders(customer_email);
                CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
                CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at);
                CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
                CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id);
                CREATE INDEX IF NOT EXISTS idx_inventory_stock_quantity ON inventory(stock_quantity);
            """)
            
            conn.commit()