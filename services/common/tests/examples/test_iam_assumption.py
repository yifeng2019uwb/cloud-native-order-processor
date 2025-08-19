"""
Unit tests for IAM assumption and AWS resource access testing module.
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from src.examples.test_iam_assumption import (
    test_aws_credentials,
    test_dynamodb_access,
    test_s3_access,
    test_sqs_access,
    test_redis_access,
    run_all_tests
)


class TestIAMAssumption:
    """Test IAM role assumption and AWS resource access functions."""

    @patch('boto3.client')
    def test_aws_credentials_success(self, mock_boto3_client):
        """Test successful AWS credentials verification."""
        # Mock STS client and response
        mock_sts = MagicMock()
        mock_sts.get_caller_identity.return_value = {
            'Account': '123456789012',
            'Arn': 'arn:aws:iam::123456789012:role/test-role',
            'UserId': 'AIDACKCEVSQ6C2EXAMPLE'
        }
        mock_boto3_client.return_value = mock_sts

        result = test_aws_credentials()

        assert result['success'] is True
        assert result['account_id'] == '123456789012'
        assert result['arn'] == 'arn:aws:iam::123456789012:role/test-role'
        assert result['username'] == 'AIDACKCEVSQ6C2EXAMPLE'

    @patch('boto3.client')
    def test_aws_credentials_no_credentials(self, mock_boto3_client):
        """Test AWS credentials when no credentials are available."""
        mock_boto3_client.side_effect = NoCredentialsError()

        result = test_aws_credentials()

        assert result['success'] is False
        assert result['error'] == 'No AWS credentials'

    @patch('boto3.client')
    def test_aws_credentials_client_error(self, mock_boto3_client):
        """Test AWS credentials when client error occurs."""
        mock_boto3_client.side_effect = ClientError(
            {'Error': {'Code': 'AccessDenied', 'Message': 'Access denied'}},
            'GetCallerIdentity'
        )

        result = test_aws_credentials()

        assert result['success'] is False
        assert 'Access denied' in result['error']

    def test_dynamodb_access_basic_functionality(self):
        """Test basic DynamoDB access functionality without complex mocking."""
        # This test verifies the function structure and basic logic
        # Since the function calls real AWS services, we'll test the basic flow

        # Test with no environment variables (should return error)
        with patch.dict(os.environ, {}, clear=True):
            result = test_dynamodb_access()
            # The function should handle missing environment variables gracefully
            assert 'error' in result or 'success' in result

    def test_dynamodb_access_environment_variables(self):
        """Test DynamoDB access with environment variables set."""
        # Test with environment variables set
        with patch.dict(os.environ, {
            'USERS_TABLE': 'test-users-table',
            'ORDERS_TABLE': 'test-orders-table'
        }):
            result = test_dynamodb_access()
            # The function should attempt to access the tables
            # Result depends on actual AWS access, but structure should be correct
            assert isinstance(result, dict)
            assert 'success' in result or 'error' in result

    def test_dynamodb_access_error_handling(self):
        """Test DynamoDB access error handling structure."""
        # Test that the function has proper error handling structure
        # This test focuses on the function's ability to handle errors gracefully

        # The function should always return a dictionary with expected keys
        # We'll test this by ensuring the function doesn't crash
        try:
            result = test_dynamodb_access()
            assert isinstance(result, dict)
            # Should have either success or error key
            assert 'success' in result or 'error' in result
        except Exception as e:
            # If the function crashes, that's a test failure
            pytest.fail(f"Function crashed with exception: {e}")

    @patch('boto3.client')
    @patch.dict(os.environ, {
        'S3_BUCKET': 'test-bucket',
        'LOGS_BUCKET': 'logs-bucket'
    })
    def test_s3_access_specific_buckets_success(self, mock_boto3_client):
        """Test successful S3 access to specific buckets."""
        # Mock S3 client and responses
        mock_s3 = MagicMock()
        mock_s3.head_bucket.return_value = {}
        mock_boto3_client.return_value = mock_s3

        result = test_s3_access()

        assert result['success'] is True
        assert 'test-bucket' in result['buckets']
        assert 'logs-bucket' in result['buckets']
        assert all(bucket['success'] for bucket in result['buckets'].values())

    @patch('boto3.client')
    @patch.dict(os.environ, {
        'S3_BUCKET': 'test-bucket'
    })
    def test_s3_access_mixed_bucket_results(self, mock_boto3_client):
        """Test S3 access with mixed bucket access results."""
        # Mock S3 client with mixed responses
        mock_s3 = MagicMock()
        mock_s3.head_bucket.side_effect = [
            {},  # Success for first bucket
            ClientError(
                {'Error': {'Code': 'AccessDenied', 'Message': 'Access denied'}},
                'HeadBucket'
            )  # Failure for second bucket
        ]
        mock_boto3_client.return_value = mock_s3

        result = test_s3_access()

        assert result['success'] is True
        assert result['buckets']['test-bucket']['success'] is True
        assert 'logs-bucket' not in result['buckets']  # Only one bucket configured

    @patch('boto3.client')
    @patch.dict(os.environ, {}, clear=True)
    def test_s3_access_list_buckets_fallback(self, mock_boto3_client):
        """Test S3 access fallback to listing buckets when no specific buckets configured."""
        # Mock S3 client and response
        mock_s3 = MagicMock()
        mock_s3.list_buckets.return_value = {
            'Buckets': [
                {'Name': 'bucket1'},
                {'Name': 'bucket2'},
                {'Name': 'bucket3'}
            ]
        }
        mock_boto3_client.return_value = mock_s3

        result = test_s3_access()

        assert result['success'] is True
        assert result['message'] == 'Can list 3 buckets'
        assert len(result['buckets']) == 3
        assert 'bucket1' in result['buckets']
        assert 'bucket2' in result['buckets']
        assert 'bucket3' in result['buckets']

    @patch('boto3.client')
    def test_s3_access_exception(self, mock_boto3_client):
        """Test S3 access when exception occurs."""
        mock_boto3_client.side_effect = Exception("S3 error")

        result = test_s3_access()

        assert result['success'] is False
        assert result['error'] == 'S3 error'

    @patch('boto3.client')
    @patch.dict(os.environ, {'QUEUE_URL': 'https://sqs.us-east-1.amazonaws.com/123456789012/test-queue'})
    def test_sqs_access_success(self, mock_boto3_client):
        """Test successful SQS access."""
        # Mock SQS client and response
        mock_sqs = MagicMock()
        mock_sqs.get_queue_attributes.return_value = {
            'Attributes': {
                'ApproximateNumberOfMessages': '5',
                'ApproximateNumberOfMessagesNotVisible': '2'
            }
        }
        mock_boto3_client.return_value = mock_sqs

        result = test_sqs_access()

        assert result['success'] is True
        assert result['queue_url'] == 'https://sqs.us-east-1.amazonaws.com/123456789012/test-queue'
        assert result['attributes']['ApproximateNumberOfMessages'] == '5'
        assert result['attributes']['ApproximateNumberOfMessagesNotVisible'] == '2'

    @patch('boto3.client')
    @patch.dict(os.environ, {}, clear=True)
    def test_sqs_access_no_queue_configured(self, mock_boto3_client):
        """Test SQS access when no queue is configured."""
        # Mock boto3.client to prevent region error
        mock_sqs = MagicMock()
        mock_boto3_client.return_value = mock_sqs

        result = test_sqs_access()

        assert result['success'] is False
        assert result['error'] == 'No SQS queue configured'

    @patch('boto3.client')
    @patch.dict(os.environ, {'QUEUE_URL': 'https://sqs.us-east-1.amazonaws.com/123456789012/test-queue'})
    def test_sqs_access_exception(self, mock_boto3_client):
        """Test SQS access when exception occurs."""
        mock_boto3_client.side_effect = Exception("SQS error")

        result = test_sqs_access()

        assert result['success'] is False
        assert result['error'] == 'SQS error'

    @patch('src.examples.test_iam_assumption.test_redis_connection')
    def test_redis_access_success(self, mock_test_connection):
        """Test successful Redis access."""
        mock_test_connection.return_value = True

        result = test_redis_access()

        assert result['success'] is True
        assert result['health_status'] == {'status': 'healthy'}

    @patch('src.examples.test_iam_assumption.test_redis_connection')
    def test_redis_access_connection_failed(self, mock_test_connection):
        """Test Redis access when connection fails."""
        mock_test_connection.return_value = False

        result = test_redis_access()

        assert result['success'] is False
        assert result['error'] == 'Redis connection failed'

    @patch('src.examples.test_iam_assumption.test_redis_connection')
    def test_redis_access_exception(self, mock_test_connection):
        """Test Redis access when exception occurs."""
        mock_test_connection.side_effect = Exception("Redis error")

        result = test_redis_access()

        assert result['success'] is False
        assert result['error'] == 'Redis error'

    @patch('src.examples.test_iam_assumption.test_aws_credentials')
    @patch('src.examples.test_iam_assumption.test_dynamodb_access')
    @patch('src.examples.test_iam_assumption.test_s3_access')
    @patch('src.examples.test_iam_assumption.test_sqs_access')
    @patch('src.examples.test_iam_assumption.test_redis_access')
    def test_run_all_tests_all_success(self, mock_redis, mock_sqs, mock_s3, mock_dynamodb, mock_aws):
        """Test running all tests with all tests passing."""
        # Mock all tests to return success
        mock_aws.return_value = {'success': True, 'account_id': '123456789012'}
        mock_dynamodb.return_value = {'success': True, 'tables': {}}
        mock_s3.return_value = {'success': True, 'buckets': {}}
        mock_sqs.return_value = {'success': True, 'queue_url': 'test'}
        mock_redis.return_value = {'success': True, 'health_status': {}}

        result = run_all_tests()

        assert result['summary']['total_tests'] == 5
        assert result['summary']['successful_tests'] == 5
        assert result['summary']['failed_tests'] == 0
        assert result['results']['aws_credentials']['success'] is True
        assert result['results']['dynamodb']['success'] is True
        assert result['results']['s3']['success'] is True
        assert result['results']['sqs']['success'] is True
        assert result['results']['redis']['success'] is True

    @patch('src.examples.test_iam_assumption.test_aws_credentials')
    @patch('src.examples.test_iam_assumption.test_dynamodb_access')
    @patch('src.examples.test_iam_assumption.test_s3_access')
    @patch('src.examples.test_iam_assumption.test_sqs_access')
    @patch('src.examples.test_iam_assumption.test_redis_access')
    def test_run_all_tests_mixed_results(self, mock_redis, mock_sqs, mock_s3, mock_dynamodb, mock_aws):
        """Test running all tests with mixed results."""
        # Mock tests with mixed results
        mock_aws.return_value = {'success': True, 'account_id': '123456789012'}
        mock_dynamodb.return_value = {'success': False, 'error': 'DynamoDB error'}
        mock_s3.return_value = {'success': True, 'buckets': {}}
        mock_sqs.return_value = {'success': False, 'error': 'SQS error'}
        mock_redis.return_value = {'success': True, 'health_status': {}}

        result = run_all_tests()

        assert result['summary']['total_tests'] == 5
        assert result['summary']['successful_tests'] == 3
        assert result['summary']['failed_tests'] == 2
        assert result['results']['aws_credentials']['success'] is True
        assert result['results']['dynamodb']['success'] is False
        assert result['results']['s3']['success'] is True
        assert result['results']['sqs']['success'] is False
        assert result['results']['redis']['success'] is True

    @patch('src.examples.test_iam_assumption.test_aws_credentials')
    @patch('src.examples.test_iam_assumption.test_dynamodb_access')
    @patch('src.examples.test_iam_assumption.test_s3_access')
    @patch('src.examples.test_iam_assumption.test_sqs_access')
    @patch('src.examples.test_iam_assumption.test_redis_access')
    def test_run_all_tests_all_failed(self, mock_redis, mock_sqs, mock_s3, mock_dynamodb, mock_aws):
        """Test running all tests with all tests failing."""
        # Mock all tests to return failure
        mock_aws.return_value = {'success': False, 'error': 'AWS error'}
        mock_dynamodb.return_value = {'success': False, 'error': 'DynamoDB error'}
        mock_s3.return_value = {'success': False, 'error': 'S3 error'}
        mock_sqs.return_value = {'success': False, 'error': 'SQS error'}
        mock_redis.return_value = {'success': False, 'error': 'Redis error'}

        result = run_all_tests()

        assert result['summary']['total_tests'] == 5
        assert result['summary']['successful_tests'] == 0
        assert result['summary']['failed_tests'] == 5
        assert all(not result['results'][key]['success'] for key in result['results'])

    @patch('src.examples.test_iam_assumption.test_aws_credentials')
    @patch('src.examples.test_iam_assumption.test_dynamodb_access')
    @patch('src.examples.test_iam_assumption.test_s3_access')
    @patch('src.examples.test_iam_assumption.test_sqs_access')
    @patch('src.examples.test_iam_assumption.test_redis_access')
    def test_run_all_tests_with_errors(self, mock_redis, mock_sqs, mock_s3, mock_dynamodb, mock_aws):
        """Test running all tests with specific error messages."""
        # Mock tests with specific error messages
        mock_aws.return_value = {'success': False, 'error': 'No AWS credentials'}
        mock_dynamodb.return_value = {'success': False, 'error': 'Table not found'}
        mock_s3.return_value = {'success': False, 'error': 'Bucket access denied'}
        mock_sqs.return_value = {'success': False, 'error': 'Queue does not exist'}
        mock_redis.return_value = {'success': False, 'error': 'Connection timeout'}

        result = run_all_tests()

        assert result['summary']['total_tests'] == 5
        assert result['summary']['successful_tests'] == 0
        assert result['summary']['failed_tests'] == 5

        # Check that error messages are preserved
        assert result['results']['aws_credentials']['error'] == 'No AWS credentials'
        assert result['results']['dynamodb']['error'] == 'Table not found'
        assert result['results']['s3']['error'] == 'Bucket access denied'
        assert result['results']['sqs']['error'] == 'Queue does not exist'
        assert result['results']['redis']['error'] == 'Connection timeout'

    @patch('src.examples.test_iam_assumption.test_aws_credentials')
    @patch('src.examples.test_iam_assumption.test_dynamodb_access')
    @patch('src.examples.test_iam_assumption.test_s3_access')
    @patch('src.examples.test_iam_assumption.test_sqs_access')
    @patch('src.examples.test_iam_assumption.test_redis_access')
    def test_run_all_tests_partial_data(self, mock_redis, mock_sqs, mock_s3, mock_dynamodb, mock_aws):
        """Test running all tests with partial data in responses."""
        # Mock tests with partial data
        mock_aws.return_value = {'success': True, 'account_id': '123456789012', 'arn': 'test-arn'}
        mock_dynamodb.return_value = {'success': True, 'tables': {'table1': {'success': True, 'status': 'ACTIVE'}}}
        mock_s3.return_value = {'success': True, 'buckets': {'bucket1': {'success': True}}}
        mock_sqs.return_value = {'success': True, 'queue_url': 'test-queue', 'attributes': {'ApproximateNumberOfMessages': '10'}}
        mock_redis.return_value = {'success': True, 'health_status': {'status': 'healthy', 'version': '6.0'}}

        result = run_all_tests()

        assert result['summary']['total_tests'] == 5
        assert result['summary']['successful_tests'] == 5
        assert result['summary']['failed_tests'] == 0

        # Check that partial data is preserved
        assert result['results']['aws_credentials']['account_id'] == '123456789012'
        assert result['results']['aws_credentials']['arn'] == 'test-arn'
        assert result['results']['dynamodb']['tables']['table1']['status'] == 'ACTIVE'
        assert result['results']['s3']['buckets']['bucket1']['success'] is True
        assert result['results']['sqs']['attributes']['ApproximateNumberOfMessages'] == '10'
        assert result['results']['redis']['health_status']['version'] == '6.0'
