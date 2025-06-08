"""Common database queries used across services"""


class OrderQueries:
    CREATE_ORDER = """
        INSERT INTO orders.orders 
        (order_id, customer_id, customer_email, customer_name, status, total_amount, shipping_address, created_at, updated_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $8)
    """

    CREATE_ORDER_ITEM = """
        INSERT INTO orders.order_items 
        (order_id, product_id, quantity, unit_price, line_total)
        VALUES ($1, $2, $3, $4, $5)
    """

    GET_ORDER = "SELECT * FROM orders.orders WHERE order_id = $1"

    GET_ORDER_ITEMS = """
        SELECT oi.*, p.name as product_name 
        FROM orders.order_items oi
        JOIN products.products p ON oi.product_id = p.product_id
        WHERE oi.order_id = $1
    """

    UPDATE_ORDER_STATUS = """
        UPDATE orders.orders 
        SET status = $1, updated_at = $2 
        WHERE order_id = $3
    """

    LIST_ORDERS = "SELECT * FROM orders.orders WHERE 1=1"


class ProductQueries:
    GET_PRODUCT = "SELECT * FROM products.products WHERE product_id = $1"
    LIST_PRODUCTS = "SELECT * FROM products.products ORDER BY name LIMIT $1"
    LIST_PRODUCTS_BY_CATEGORY = (
        "SELECT * FROM products.products WHERE category = $1 ORDER BY name LIMIT $2"
    )


class InventoryQueries:
    GET_INVENTORY = "SELECT * FROM inventory.inventory WHERE product_id = $1"

    RESERVE_STOCK = """
        UPDATE inventory.inventory 
        SET reserved_quantity = reserved_quantity + $1, updated_at = $2
        WHERE product_id = $3
    """

    RELEASE_STOCK = """
        UPDATE inventory.inventory 
        SET reserved_quantity = GREATEST(0, reserved_quantity - $1), updated_at = $2
        WHERE product_id = $3
    """

    UPDATE_STOCK = """
        UPDATE inventory.inventory 
        SET stock_quantity = stock_quantity + $1, updated_at = $2
        WHERE product_id = $3
    """
