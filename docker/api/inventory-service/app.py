from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
import os
from models import Product
from database import PostgreSQLManager

app = Flask(__name__)
CORS(app)

db_manager = PostgreSQLManager()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "inventory-service"})

@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        products = db_manager.get_products()
        return jsonify({'products': products})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<product_id>', methods=['GET'])
def get_product(product_id):
    try:
        product = db_manager.get_product(product_id)
        if product:
            return jsonify(product)
        return jsonify({'error': 'Product not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products', methods=['POST'])
def create_product():
    try:
        data = request.get_json()
        product = Product(
            product_id=data['product_id'],
            name=data['name'],
            description=data['description'],
            price=data['price'],
            category=data['category']
        )
        db_manager.create_product(product, data.get('initial_stock', 0))
        return jsonify({'message': 'Product created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<product_id>/stock', methods=['PUT'])
def update_stock(product_id):
    try:
        data = request.get_json()
        quantity_change = data['quantity_change']
        success = db_manager.update_stock(product_id, quantity_change)
        if success:
            return jsonify({'message': 'Stock updated successfully'})
        return jsonify({'error': 'Product not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<product_id>/reserve', methods=['POST'])
def reserve_stock(product_id):
    try:
        data = request.get_json()
        quantity = data['quantity']
        success = db_manager.reserve_stock(product_id, quantity)
        if success:
            return jsonify({'message': 'Stock reserved'})
        return jsonify({'error': 'Insufficient stock'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<product_id>/release', methods=['POST'])
def release_stock(product_id):
    try:
        data = request.get_json()
        quantity = data['quantity']
        success = db_manager.release_reserved_stock(product_id, quantity)
        if success:
            return jsonify({'message': 'Reserved stock released'})
        return jsonify({'error': 'Failed to release stock'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/low-stock', methods=['GET'])
def get_low_stock_products():
    try:
        products = db_manager.get_low_stock_products()
        return jsonify({'products': products})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Initialize database on startup
    db_manager.initialize_database()
    app.run(host='0.0.0.0', port=5001, debug=True)