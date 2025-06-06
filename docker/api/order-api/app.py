from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
import json
import uuid
from datetime import datetime
import os
from models import Order
from database import DynamoDBManager

app = Flask(__name__)
CORS(app)

# Initialize DynamoDB
db_manager = DynamoDBManager()
sqs = boto3.client('sqs', region_name=os.getenv('AWS_REGION', 'us-west-2'))

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "order-api"})

@app.route('/api/orders', methods=['POST'])
def create_order():
    try:
        data = request.get_json()
        
        # Create order
        order = Order(
            order_id=str(uuid.uuid4()),
            customer_email=data['customer_email'],
            customer_name=data['customer_name'],
            items=data['items'],
            total_amount=data['total_amount'],
            status='pending',
            created_at=datetime.utcnow().isoformat()
        )
        
        # Save to DynamoDB
        db_manager.create_order(order)
        
        # Send to payment processing queue
        sqs.send_message(
            QueueUrl=os.getenv('PAYMENT_QUEUE_URL'),
            MessageBody=json.dumps({
                'order_id': order.order_id,
                'amount': order.total_amount,
                'customer_email': order.customer_email
            })
        )
        
        return jsonify({
            'order_id': order.order_id,
            'status': 'created',
            'message': 'Order created successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    try:
        order = db_manager.get_order(order_id)
        if order:
            return jsonify(order)
        return jsonify({'error': 'Order not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders', methods=['GET'])
def list_orders():
    try:
        orders = db_manager.list_orders()
        return jsonify({'orders': orders})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders/<order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    try:
        data = request.get_json()
        db_manager.update_order_status(order_id, data['status'])
        return jsonify({'message': 'Order status updated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)