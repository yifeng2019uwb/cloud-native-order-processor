import json
import os
from datetime import datetime
from typing import Dict, Any
import uuid
from decimal import Decimal

from postgresql_manager import PostgreSQLManager
from models import Order, OrderItem, Product, PaymentTransaction
from order_app import OrderProcessor
from inventory_app import InventoryManager

# Initialize managers
db_manager = PostgreSQLManager()
order_processor = OrderProcessor(db_manager)
inventory_manager = InventoryManager(db_manager)

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    """Main Lambda handler for the order processing API"""
    
    try:
        # Extract request information
        http_method = event.get('httpMethod', '')
        path = event.get('path', '')
        query_params = event.get('queryStringParameters') or {}
        body = event.get('body', '{}')
        
        # Parse body if it's a string
        if isinstance(body, str):
            try:
                body = json.loads(body) if body else {}
            except json.JSONDecodeError:
                return create_response(400, {'error': 'Invalid JSON in request body'})
        
        # Route the request
        if path.startswith('/orders'):
            return handle_orders(http_method, path, query_params, body)
        elif path.startswith('/products') or path.startswith('/inventory'):
            return handle_inventory(http_method, path, query_params, body)
        elif path.startswith('/health'):
            return handle_health()
        else:
            return create_response(404, {'error': 'Endpoint not found'})
            
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})

def handle_orders(method: str, path: str, query_params: Dict, body: Dict) -> Dict:
    """Handle order-related requests"""
    
    try:
        if method == 'POST' and path == '/orders':
            # Create new order
            return create_order(body)
            
        elif method == 'GET' and path == '/orders':
            # List orders
            limit = int(query_params.get('limit', 50))
            orders = order_processor.list_orders(limit)
            return create_response(200, {'orders': orders})
            
        elif method == 'GET' and path.startswith('/orders/'):
            # Get specific order
            order_id = path.split('/')[-1]
            order = order_processor.get_order(order_id)
            if order:
                return create_response(200, {'order': order})
            else:
                return create_response(404, {'error': 'Order not found'})
                
        elif method == 'PUT' and path.startswith('/orders/') and path.endswith('/status'):
            # Update order status
            order_id = path.split('/')[-2]
            new_status = body.get('status')
            if not new_status:
                return create_response(400, {'error': 'Status is required'})
                
            success = order_processor.update_order_status(order_id, new_status)
            if success:
                return create_response(200, {'message': 'Order status updated'})
            else:
                return create_response(404, {'error': 'Order not found'})
                
        elif method == 'POST' and path.startswith('/orders/') and path.endswith('/payment'):
            # Process payment
            order_id = path.split('/')[-2]
            return process_payment(order_id, body)
            
        else:
            return create_response(405, {'error': 'Method not allowed'})
            
    except Exception as e:
        print(f"Error handling orders: {str(e)}")
        return create_response(500, {'error': 'Failed to process order request'})

def handle_inventory(method: str, path: str, query_params: Dict, body: Dict) -> Dict:
    """Handle inventory and product-related requests"""
    
    try:
        if method == 'GET' and path == '/products':
            # List products
            limit = int(query_params.get('limit', 50))
            products = inventory_manager.get_products(limit)
            return create_response(200, {'products': products})
            
        elif method == 'GET' and path.startswith('/products/'):
            # Get specific product
            product_id = path.split('/')[-1]
            product = inventory_manager.get_product(product_id)
            if product:
                return create_response(200, {'product': product})
            else:
                return create_response(404, {'error': 'Product not found'})
                
        elif method == 'POST' and path == '/products':
            # Create new product
            return create_product(body)
            
        elif method == 'PUT' and path.startswith('/inventory/') and path.endswith('/stock'):
            # Update stock
            product_id = path.split('/')[-2]
            quantity_change = body.get('quantity_change', 0)
            
            success = inventory_manager.update_stock(product_id, quantity_change)
            if success:
                return create_response(200, {'message': 'Stock updated'})
            else:
                return create_response(404, {'error': 'Product not found'})
                
        elif method == 'POST' and path.startswith('/inventory/') and path.endswith('/reserve'):
            # Reserve stock
            product_id = path.split('/')[-2]
            quantity = body.get('quantity', 0)
            
            success = inventory_manager.reserve_stock(product_id, quantity)
            if success:
                return create_response(200, {'message': 'Stock reserved'})
            else:
                return create_response(400, {'error': 'Insufficient stock'})
                
        else:
            return create_response(405, {'error': 'Method not allowed'})
            
    except Exception as e:
        print(f"Error handling inventory: {str(e)}")
        return create_response(500, {'error': 'Failed to process inventory request'})

def create_order(body: Dict) -> Dict:
    """Create a new order"""
    
    required_fields = ['customer_email', 'customer_name', 'items']
    for field in required_fields:
        if field not in body:
            return create_response(400, {'error': f'Missing required field: {field}'})
    
    # Validate items
    items = body['items']
    if not items or not isinstance(items, list):
        return create_response(400, {'error': 'Items must be a non-empty list'})
    
    # Calculate total amount and validate items
    total_amount = 0
    validated_items = []
    
    for item in items:
        if not all(k in item for k in ['product_id', 'quantity']):
            return create_response(400, {'error': 'Each item must have product_id and quantity'})
        
        # Get product details
        product = inventory_manager.get_product(item['product_id'])
        if not product:
            return create_response(400, {'error': f'Product {item["product_id"]} not found'})
        
        quantity = int(item['quantity'])
        price = float(product['price'])
        
        validated_items.append({
            'product_id': item['product_id'],
            'product_name': product['name'],
            'quantity': quantity,
            'price': price
        })
        
        total_amount += quantity * price
    
    # Create order object
    order = Order(
        order_id=str(uuid.uuid4()),
        customer_email=body['customer_email'],
        customer_name=body['customer_name'],
        items=validated_items,
        total_amount=total_amount,
        status='pending',
        created_at=datetime.utcnow().isoformat()
    )
    
    # Save order
    success = order_processor.create_order(order)
    if success:
        return create_response(201, {'order': order.to_dict()})
    else:
        return create_response(500, {'error': 'Failed to create order'})

def create_product(body: Dict) -> Dict:
    """Create a new product"""
    
    required_fields = ['name', 'price', 'category']
    for field in required_fields:
        if field not in body:
            return create_response(400, {'error': f'Missing required field: {field}'})
    
    product = Product(
        product_id=str(uuid.uuid4()),
        name=body['name'],
        description=body.get('description', ''),
        price=float(body['price']),
        category=body['category'],
        created_at=datetime.utcnow().isoformat()
    )
    
    success = inventory_manager.create_product(product)
    if success:
        return create_response(201, {'product': product.__dict__})
    else:
        return create_response(500, {'error': 'Failed to create product'})

def process_payment(order_id: str, body: Dict) -> Dict:
    """Process payment for an order"""
    
    required_fields = ['amount', 'payment_method']
    for field in required_fields:
        if field not in body:
            return create_response(400, {'error': f'Missing required field: {field}'})
    
    # Get order
    order = order_processor.get_order(order_id)
    if not order:
        return create_response(404, {'error': 'Order not found'})
    
    # Validate payment amount
    if float(body['amount']) != float(order['total_amount']):
        return create_response(400, {'error': 'Payment amount does not match order total'})
    
    # Create payment transaction
    transaction = PaymentTransaction(
        transaction_id=str(uuid.uuid4()),
        order_id=order_id,
        amount=float(body['amount']),
        status='completed',  # In real implementation, this would be based on payment gateway response
        payment_method=body['payment_method'],
        gateway_response={'simulated': True},
        created_at=datetime.utcnow().isoformat()
    )
    
    # Process payment (simplified)
    success = order_processor.process_payment(transaction)
    if success:
        # Update order status
        order_processor.update_order_status(order_id, 'paid')
        return create_response(200, {'transaction': transaction.__dict__})
    else:
        return create_response(500, {'error': 'Payment processing failed'})

def handle_health() -> Dict:
    """Health check endpoint"""
    return create_response(200, {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'order-processor-api'
    })

def create_response(status_code: int, body: Any) -> Dict:
    """Create a standard API response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        },
        'body': json.dumps(body, cls=DecimalEncoder)
    }

# Initialize database on first import
try:
    db_manager.initialize_database()
except Exception as e:
    print(f"Warning: Failed to initialize database: {str(e)}")