#!/usr/bin/env python3
"""
Test IAM role assumption and AWS resource access
Verifies that the service can access DynamoDB, S3, SQS, and Redis
"""

import os
import boto3
import logging
from typing import Dict, Any
from botocore.exceptions import ClientError, NoCredentialsError

from ..database.redis_connection import test_redis_connection, get_redis_health_status

logger = logging.getLogger(__name__)

def test_aws_credentials() -> Dict[str, Any]:
    """Test AWS credentials and role assumption"""
    try:
        # Test STS to get caller identity
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()

        logger.info(f"AWS Account ID: {identity['Account']}")
        logger.info(f"User/Role ARN: {identity['Arn']}")
        logger.info(f"User ID: {identity['UserId']}")

        return {
            "success": True,
            "account_id": identity['Account'],
            "arn": identity['Arn'],
            "user_id": identity['UserId']
        }
    except NoCredentialsError:
        logger.error("No AWS credentials found")
        return {"success": False, "error": "No AWS credentials"}
    except ClientError as e:
        logger.error(f"AWS credentials error: {e}")
        return {"success": False, "error": str(e)}

def test_dynamodb_access() -> Dict[str, Any]:
    """Test DynamoDB access"""
    try:
        dynamodb = boto3.client('dynamodb')

        # Get table names from environment
        tables = []
        for env_var in ['USERS_TABLE', 'ORDERS_TABLE', 'INVENTORY_TABLE']:
            table_name = os.getenv(env_var)
            if table_name:
                tables.append(table_name)

        if not tables:
            return {"success": False, "error": "No DynamoDB tables configured"}

        # Test describe table for each table
        results = {}
        for table_name in tables:
            try:
                response = dynamodb.describe_table(TableName=table_name)
                results[table_name] = {
                    "success": True,
                    "status": response['Table']['TableStatus']
                }
            except ClientError as e:
                results[table_name] = {
                    "success": False,
                    "error": str(e)
                }

        return {
            "success": True,
            "tables": results
        }
    except Exception as e:
        logger.error(f"DynamoDB test error: {e}")
        return {"success": False, "error": str(e)}

def test_s3_access() -> Dict[str, Any]:
    """Test S3 access"""
    try:
        s3 = boto3.client('s3')

        # Get bucket names from environment or use defaults
        buckets = []
        for env_var in ['S3_BUCKET', 'LOGS_BUCKET']:
            bucket_name = os.getenv(env_var)
            if bucket_name:
                buckets.append(bucket_name)

        if not buckets:
            # Try to list buckets to test basic access
            response = s3.list_buckets()
            return {
                "success": True,
                "message": f"Can list {len(response['Buckets'])} buckets",
                "buckets": [b['Name'] for b in response['Buckets'][:5]]  # First 5 buckets
            }

        # Test access to specific buckets
        results = {}
        for bucket_name in buckets:
            try:
                response = s3.head_bucket(Bucket=bucket_name)
                results[bucket_name] = {"success": True}
            except ClientError as e:
                results[bucket_name] = {"success": False, "error": str(e)}

        return {
            "success": True,
            "buckets": results
        }
    except Exception as e:
        logger.error(f"S3 test error: {e}")
        return {"success": False, "error": str(e)}

def test_sqs_access() -> Dict[str, Any]:
    """Test SQS access"""
    try:
        sqs = boto3.client('sqs')

        # Get queue URL from environment
        queue_url = os.getenv('QUEUE_URL')
        if not queue_url:
            return {"success": False, "error": "No SQS queue configured"}

        # Test get queue attributes
        response = sqs.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=['All']
        )

        return {
            "success": True,
            "queue_url": queue_url,
            "attributes": {
                "ApproximateNumberOfMessages": response['Attributes'].get('ApproximateNumberOfMessages', 'N/A'),
                "ApproximateNumberOfMessagesNotVisible": response['Attributes'].get('ApproximateNumberOfMessagesNotVisible', 'N/A')
            }
        }
    except Exception as e:
        logger.error(f"SQS test error: {e}")
        return {"success": False, "error": str(e)}

def test_redis_access() -> Dict[str, Any]:
    """Test Redis access"""
    try:
        # Test Redis connection
        if test_redis_connection():
            health_status = get_redis_health_status()
            return {
                "success": True,
                "health_status": health_status
            }
        else:
            return {"success": False, "error": "Redis connection failed"}
    except Exception as e:
        logger.error(f"Redis test error: {e}")
        return {"success": False, "error": str(e)}

def run_all_tests() -> Dict[str, Any]:
    """Run all AWS resource tests"""
    logger.info("🚀 Starting AWS resource access tests...")

    results = {
        "aws_credentials": test_aws_credentials(),
        "dynamodb": test_dynamodb_access(),
        "s3": test_s3_access(),
        "sqs": test_sqs_access(),
        "redis": test_redis_access()
    }

    # Summary
    successful_tests = sum(1 for result in results.values() if result.get("success", False))
    total_tests = len(results)

    logger.info(f"📊 Test Results: {successful_tests}/{total_tests} successful")

    for test_name, result in results.items():
        status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
        logger.info(f"  {test_name}: {status}")
        if not result.get("success", False):
            logger.error(f"    Error: {result.get('error', 'Unknown error')}")

    return {
        "summary": {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": total_tests - successful_tests
        },
        "results": results
    }

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Run tests
    test_results = run_all_tests()

    # Print summary
    summary = test_results["summary"]
    print(f"\n🎯 Test Summary:")
    print(f"   Total Tests: {summary['total_tests']}")
    print(f"   Successful: {summary['successful_tests']}")
    print(f"   Failed: {summary['failed_tests']}")

    if summary['failed_tests'] > 0:
        print(f"\n❌ Some tests failed. Check the logs above for details.")
        exit(1)
    else:
        print(f"\n✅ All tests passed!")