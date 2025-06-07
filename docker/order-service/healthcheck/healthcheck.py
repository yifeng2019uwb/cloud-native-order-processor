#!/usr/bin/env python3
"""
Health check script for order service container
"""

import sys
import requests
import psycopg2
import redis
import boto3
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_http_endpoint():
    """Check if the main HTTP endpoint is responding"""
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            logger.info("HTTP endpoint check: PASSED")
            return True
        else:
            logger.error(f"HTTP endpoint check: FAILED - Status code: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"HTTP endpoint check: FAILED - {str(e)}")
        return False

def check_database_connection():
    """Check database connectivity"""
    try:
        database_url = os.getenv('DATABASE_URL', 'postgresql://orderuser:orderpass@postgres:5432/orderdb')
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        cursor.fetchone()
        cursor.close()
        conn.close()
        logger.info("Database connection check: PASSED")
        return True
    except Exception as e:
        logger.error(f"Database connection check: FAILED - {str(e)}")
        return False

def check_redis_connection():
    """Check Redis connectivity"""
    try:
        redis_url = os.getenv('REDIS_URL', 'redis://redis:6379/0')
        r = redis.from_url(redis_url)
        r.ping()
        logger.info("Redis connection check: PASSED")
        return True
    except Exception as e:
        logger.error(f"Redis connection check: FAILED - {str(e)}")
        return False

def check_aws_services():
    """Check AWS SNS/SQS connectivity"""
    try:
        # Configure AWS client for LocalStack
        endpoint_url = os.getenv('AWS_ENDPOINT_URL', 'http://localstack:4566')
        region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        
        # Test SNS
        sns_client = boto3.client(
            'sns',
            endpoint_url=endpoint_url,
            region_name=region,
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'test'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'test')
        )
        
        # Test SQS
        sqs_client = boto3.client(
            'sqs',
            endpoint_url=endpoint_url,
            region_name=region,
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'test'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'test')
        )
        
        # Try to list topics and queues
        sns_client.list_topics()
        sqs_client.list_queues()
        
        logger.info("AWS services connection check: PASSED")
        return True
    except Exception as e:
        logger.error(f"AWS services connection check: FAILED - {str(e)}")
        return False

def main():
    """Run all health checks"""
    checks = [
        check_http_endpoint,
        check_database_connection,
        check_redis_connection,
        check_aws_services
    ]
    
    all_passed = True
    
    for check in checks:
        try:
            if not check():
                all_passed = False
        except Exception as e:
            logger.error(f"Health check failed with exception: {str(e)}")
            all_passed = False
    
    if all_passed:
        logger.info("All health checks PASSED")
        sys.exit(0)
    else:
        logger.error("Some health checks FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()