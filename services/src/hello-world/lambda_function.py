import json
import os
from datetime import datetime

def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'message': 'Hello from Lambda!',
            'timestamp': datetime.now().isoformat(),
            'environment': os.getenv('ENVIRONMENT', 'development'),
            'request_id': context.aws_request_id
        })
    }