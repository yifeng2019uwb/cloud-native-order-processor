print('Hello from dummy inventory_manager lambda')
import json

def lambda_handler(event, context):
    """Dummy order processor Lambda function"""
    print("Order processor Lambda invoked")
    print(f"Event: {json.dumps(event)}")
    
    # Dummy processing
    order_id = event.get('order_id', 'dummy-order-123')
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Order processed successfully',
            'order_id': order_id,
            'status': 'processed'
        })
    }