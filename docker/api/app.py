from flask import Flask, jsonify, request
import os

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "api"})

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({
        "message": "Hello from containerized API!",
        "environment": os.getenv('ENVIRONMENT', 'development'),
        "version": "1.0.0"
    })

@app.route('/api/data', methods=['POST'])
def post_data():
    data = request.get_json()
    return jsonify({
        "message": "Data received successfully",
        "received_data": data
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)