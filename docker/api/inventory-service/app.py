from datetime import datetime
from typing import List, Dict, Optional
import uuid

from models import Product

class InventoryManager:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def create_product(self, product: Product, initial_stock: int = 0) -> bool:
        """Create a new product and initialize its inventory"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Insert product
                cursor.execute("""
                    INSERT INTO products (product_id, name, description, price, category, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    product.product_id,
                    product.name,
                    product.description,
                    product.price,
                    product.category,
                    product.created_at,
                    product.created_at
                ))
                
                # Initialize inventory
                cursor.execute("""
                    INSERT INTO inventory (product_id, stock_quantity, reserved_quantity, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    product.product_id,
                    initial_stock,
                    0,
                    product.created_at,
                    product.created_at
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error creating product: {str(e)}")
            return False
    
    def get_products(self, limit: int = 50, category: str = None, low_stock_only: bool = False) -> List[Dict]:
        """Get products with optional filtering"""
        try:
            products = self.db.get_products(limit)
            
            # Apply filters
            if category:
                products = [p for p in products if p.get('category') == category]
            
            if low_stock_only:
                products = [
                    p for p in products 
                    if (p.get('stock_quantity', 0) - p.get('reserved_quantity', 0)) <= p.get('min_stock_level', 10)
                ]
            
            return products
            
        except Exception as e:
            print(f"Error getting products: {str(e)}")
            return []
    
    def get_product(self, product_id: str) -> Optional[Dict]:
        """Get a specific product with inventory details"""
        try:
            return self.db.get_product(product_id)
        except Exception as e:
            print(f"Error getting product {product_id}: {str(e)}")
            return None
    
    def update_product(self, product_id: str, updates: Dict) -> bool:
        """Update product information"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Build dynamic update query
                update_fields = []
                values = []
                
                allowed_fields = ['name', 'description', 'price', 'category']
                for field in allowed_fields:
                    if field in updates:
                        update_fields.append(f"{field} = %s")
                        values.append(updates[field])
                
                if not update_fields:
                    return False
                
                # Add updated_at
                update_fields.append("updated_at = %s")
                values.append(datetime.utcnow().isoformat())
                values.append(product_id)
                
                query = f"""
                    UPDATE products 
                    SET {', '.join(update_fields)}
                    WHERE product_id = %s
                """
                
                cursor.execute(query, values)
                conn.commit()
                
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"Error updating product: {str(e)}")
            return False
    
    def delete_product(self, product_id: str) -> bool:
        """Delete a product and its inventory (if no pending orders)"""
        try:
            # Check if product has any pending orders
            if self._has_pending_orders(product_id):
                print(f"Cannot delete product {product_id} - has pending orders")
                return False
            
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Delete inventory first (foreign key constraint)
                cursor.execute("DELETE FROM inventory WHERE product_id = %s", (product_id,))
                
                # Delete product
                cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"Error deleting product: {str(e)}")
            return False
    
    def update_stock(self, product_id: str, quantity_change: int, reason: str = None) -> bool:
        """Update stock quantity with audit trail"""
        try:
            success = self.db.update_stock(product_id, quantity_change)
            
            if success and reason:
                self._log_stock_movement(product_id, quantity_change, reason)
            
            return success
            
        except Exception as e:
            print(f"Error updating stock: {str(e)}")
            return False
    
    def reserve_stock(self, product_id: str, quantity: int) -> bool:
        """Reserve stock for an order"""
        try:
            return self.db.reserve_stock(product_id, quantity)
        except Exception as e:
            print(f"Error reserving stock: {str(e)}")
            return False
    
    def release_stock_reservation(self, product_id: str, quantity: int) -> bool:
        """Release reserved stock (e.g., when order is cancelled)"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE inventory 
                    SET reserved_quantity = GREATEST(0, reserved_quantity - %s),
                        updated_at = %s
                    WHERE product_id = %s
                """, (quantity, datetime.utcnow().isoformat(), product_id))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"Error releasing stock reservation: {str(e)}")
            return False
    
    def get_stock_status(self, product_id: str) -> Dict:
        """Get detailed stock status for a product"""
        try:
            product = self.get_product(product_id)
            if not product:
                return {}
            
            stock_quantity = product.get('stock_quantity', 0)
            reserved_quantity = product.get('reserved_quantity', 0)
            min_stock_level = product.get('min_stock_level', 10)
            available_quantity = stock_quantity - reserved_quantity
            
            return {
                'product_id': product_id,
                'product_name': product.get('name', ''),
                'stock_quantity': stock_quantity,
                'reserved_quantity': reserved_quantity,
                'available_quantity': available_quantity,
                'min_stock_level': min_stock_level,
                'is_low_stock': available_quantity <= min_stock_level,
                'is_out_of_stock': available_quantity <= 0,

            }
        
        except Exception as e:
            print(f"Error deleting product: {str(e)}")
            return False