# lambda_package/lambda_handler.py

"""
Lambda Proxy Handler for External FastAPI Services

This Lambda function acts as a pure proxy, forwarding API Gateway requests
to external FastAPI services via HTTP calls. It does NOT import or run
FastAPI apps inside Lambda.

Request Flow:
1. API Gateway receives HTTP request
2. Lambda handler determines target service based on path
3. Lambda forwards request to external service URL
4. External service processes request and returns response
5. Lambda forwards response back to API Gateway
"""

import os
import json
import logging
import requests
from datetime import datetime
from urllib.parse import urljoin, urlparse

# Configure logging for CloudWatch
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_service_url(path):
    """
    Determine which external service URL to use based on request path
    """
    if path.startswith('/auth'):
        user_service_url = os.environ.get('USER_SERVICE_URL')
        if not user_service_url:
            raise ValueError("USER_SERVICE_URL environment variable not set")
        return user_service_url
    elif path.startswith('/inventory'):
        inventory_service_url = os.environ.get('INVENTORY_SERVICE_URL')
        if not inventory_service_url:
            raise ValueError("INVENTORY_SERVICE_URL environment variable not set")
        return inventory_service_url
    else:
        # Default to inventory service
        inventory_service_url = os.environ.get('INVENTORY_SERVICE_URL')
        if not inventory_service_url:
            raise ValueError("INVENTORY_SERVICE_URL environment variable not set")
        return inventory_service_url

def lambda_handler(event, context):
    """
    AWS Lambda entry point - Pure HTTP proxy to external services
    """

    # Extract request details
    http_method = event.get('httpMethod', 'GET')
    path = event.get('path', '')
    headers = event.get('headers', {}) or {}
    query_string = event.get('queryStringParameters', {}) or {}
    body = event.get('body', '')

    # Determine target service URL
    base_url = get_service_url(path)

    # Log request for monitoring
    logger.info(json.dumps({
        "event": "proxy_request",
        "method": http_method,
        "path": path,
        "target_url": base_url,
        "timestamp": datetime.utcnow().isoformat(),
        "lambda_request_id": getattr(context, 'aws_request_id', 'unknown')
    }))

    try:
        # Prepare request to external service
        url = urljoin(base_url, path)

        # Prepare headers (remove Lambda-specific headers)
        proxy_headers = {}
        for key, value in headers.items():
            # Skip Lambda-specific headers
            if key.lower() not in ['x-forwarded-for', 'x-forwarded-proto', 'x-forwarded-port']:
                proxy_headers[key] = value

        # Add content-type if body exists
        if body and 'content-type' not in [k.lower() for k in proxy_headers.keys()]:
            proxy_headers['Content-Type'] = 'application/json'

        # Make request to external service
        response = requests.request(
            method=http_method,
            url=url,
            headers=proxy_headers,
            params=query_string,
            data=body,
            timeout=30  # 30 second timeout
        )

        # Prepare response for API Gateway
        response_headers = dict(response.headers)

        # Remove headers that might cause issues
        headers_to_remove = ['content-encoding', 'transfer-encoding', 'connection']
        for header in headers_to_remove:
            response_headers.pop(header, None)

        # Log successful response
        logger.info(json.dumps({
            "event": "proxy_success",
            "method": http_method,
            "path": path,
            "status_code": response.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }))

        return {
            'statusCode': response.status_code,
            'headers': response_headers,
            'body': response.text
        }

    except requests.exceptions.Timeout:
        logger.error(json.dumps({
            "event": "proxy_timeout",
            "method": http_method,
            "path": path,
            "target_url": base_url,
            "timestamp": datetime.utcnow().isoformat()
        }))

        return {
            'statusCode': 504,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                "error": "Gateway Timeout",
                "message": f"External service at {base_url} did not respond within timeout"
            })
        }

    except requests.exceptions.ConnectionError:
        logger.error(json.dumps({
            "event": "proxy_connection_error",
            "method": http_method,
            "path": path,
            "target_url": base_url,
            "timestamp": datetime.utcnow().isoformat()
        }))

        return {
            'statusCode': 502,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                "error": "Bad Gateway",
                "message": f"Cannot connect to external service at {base_url}"
            })
        }

    except Exception as e:
        logger.error(json.dumps({
            "event": "proxy_error",
            "method": http_method,
            "path": path,
            "target_url": base_url,
            "error": str(e),
            "error_type": type(e).__name__,
            "timestamp": datetime.utcnow().isoformat()
        }))

        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                "error": "Internal Server Error",
                "message": f"Proxy error: {str(e)}"
            })
        }