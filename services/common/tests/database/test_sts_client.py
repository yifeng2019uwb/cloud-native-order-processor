import pytest
from unittest.mock import Mock, patch, MagicMock
import os
from botocore.exceptions import ClientError, NoCredentialsError

from src.aws.sts_client import STSClient
from src.exceptions.shared_exceptions import InternalServerException

@pytest.fixture(autouse=True)
def clear_env(monkeypatch):
    monkeypatch.delenv('AWS_REGION', raising=False)

def test_init_success():
    """Test successful STS client initialization"""
    with patch.dict(os.environ, {'AWS_REGION': 'us-west-2'}):
        with patch('boto3.Session') as mock_session:
            mock_sess = MagicMock()
            mock_sts_client = MagicMock()
            mock_session.return_value = mock_sess
            mock_sess.client.return_value = mock_sts_client

            client = STSClient()
            assert client.region == 'us-west-2'
            assert client.session is not None
            assert client.sts_client is not None

def test_init_missing_aws_region():
    """Test initialization with missing AWS_REGION environment variable"""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(InternalServerException):
            STSClient()

def test_get_caller_identity_success():
    """Test successful get_caller_identity call"""
    with patch.dict(os.environ, {'AWS_REGION': 'us-west-2'}):
        with patch('boto3.Session') as mock_session:
            mock_sess = MagicMock()
            mock_sts_client = MagicMock()
            mock_session.return_value = mock_sess
            mock_sess.client.return_value = mock_sts_client

            client = STSClient()

            mock_response = {
                'UserId': 'AIDACKCEVSQ6C2EXAMPLE',
                'Account': '123456789012',
                'Arn': 'arn:aws:iam::123456789012:user/JohnDoe'
            }
            mock_sts_client.get_caller_identity.return_value = mock_response

            result = client.get_caller_identity()
            assert result == mock_response
            mock_sts_client.get_caller_identity.assert_called_once()

def test_get_caller_identity_no_credentials():
    """Test get_caller_identity with no credentials"""
    with patch.dict(os.environ, {'AWS_REGION': 'us-west-2'}):
        with patch('boto3.Session') as mock_session:
            mock_sess = MagicMock()
            mock_sts_client = MagicMock()
            mock_session.return_value = mock_sess
            mock_sess.client.return_value = mock_sts_client

            client = STSClient()
            mock_sts_client.get_caller_identity.side_effect = NoCredentialsError()

            with pytest.raises(InternalServerException) as exc_info:
                client.get_caller_identity()
            assert "AWS credentials not configured" in str(exc_info.value)

def test_get_caller_identity_client_error():
    """Test get_caller_identity with client error"""
    with patch.dict(os.environ, {'AWS_REGION': 'us-west-2'}):
        with patch('boto3.Session') as mock_session:
            mock_sess = MagicMock()
            mock_sts_client = MagicMock()
            mock_session.return_value = mock_sess
            mock_sess.client.return_value = mock_sts_client

            client = STSClient()
            mock_sts_client.get_caller_identity.side_effect = ClientError(
                {'Error': {'Code': 'AccessDenied', 'Message': 'Access denied'}},
                'GetCallerIdentity'
            )

            with pytest.raises(InternalServerException) as exc_info:
                client.get_caller_identity()
            assert "AWS STS error" in str(exc_info.value)

def test_assume_role_success():
    """Test successful assume_role call"""
    with patch.dict(os.environ, {'AWS_REGION': 'us-west-2'}):
        with patch('boto3.Session') as mock_session:
            mock_sess = MagicMock()
            mock_sts_client = MagicMock()
            mock_session.return_value = mock_sess
            mock_sess.client.return_value = mock_sts_client

            client = STSClient()

            mock_response = {
                'Credentials': {
                    'AccessKeyId': 'AKIAIOSFODNN7EXAMPLE',
                    'SecretAccessKey': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
                    'SessionToken': 'AQoEXAMPLEH4aoAH0gNCAPyJxz4BlCFFxWNE1OPTgk5TthT...',
                    'Expiration': '2023-01-01T12:00:00Z'
                },
                'AssumedRoleUser': {
                    'AssumedRoleId': 'AROAIFSODNN7EXAMPLE:user',
                    'Arn': 'arn:aws:sts::123456789012:assumed-role/role-name/user'
                }
            }
            mock_sts_client.assume_role.return_value = mock_response

            result = client.assume_role('arn:aws:iam::123456789012:role/test-role', 'test-session')
            assert result == mock_response
            mock_sts_client.assume_role.assert_called_once_with(
                RoleArn='arn:aws:iam::123456789012:role/test-role',
                RoleSessionName='test-session',
                DurationSeconds=3600
            )

def test_assume_role_no_credentials():
    """Test assume_role with no credentials"""
    with patch.dict(os.environ, {'AWS_REGION': 'us-west-2'}):
        with patch('boto3.Session') as mock_session:
            mock_sess = MagicMock()
            mock_sts_client = MagicMock()
            mock_session.return_value = mock_sess
            mock_sess.client.return_value = mock_sts_client

            client = STSClient()
            mock_sts_client.assume_role.side_effect = NoCredentialsError()

            with pytest.raises(InternalServerException) as exc_info:
                client.assume_role('arn:aws:iam::123456789012:role/test-role', 'test-session')
            assert "AWS credentials not configured" in str(exc_info.value)

def test_assume_role_client_error():
    """Test assume_role with client error"""
    with patch.dict(os.environ, {'AWS_REGION': 'us-west-2'}):
        with patch('boto3.Session') as mock_session:
            mock_sess = MagicMock()
            mock_sts_client = MagicMock()
            mock_session.return_value = mock_sess
            mock_sess.client.return_value = mock_sts_client

            client = STSClient()
            mock_sts_client.assume_role.side_effect = ClientError(
                {'Error': {'Code': 'AccessDenied', 'Message': 'Access denied'}},
                'AssumeRole'
            )

            with pytest.raises(InternalServerException) as exc_info:
                client.assume_role('arn:aws:iam::123456789012:role/test-role', 'test-session')
            assert "AWS STS assume role error" in str(exc_info.value)

def test_get_session_token_success():
    """Test successful get_session_token call"""
    with patch.dict(os.environ, {'AWS_REGION': 'us-west-2'}):
        with patch('boto3.Session') as mock_session:
            mock_sess = MagicMock()
            mock_sts_client = MagicMock()
            mock_session.return_value = mock_sess
            mock_sess.client.return_value = mock_sts_client

            client = STSClient()

            mock_response = {
                'Credentials': {
                    'AccessKeyId': 'AKIAIOSFODNN7EXAMPLE',
                    'SecretAccessKey': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
                    'SessionToken': 'AQoEXAMPLEH4aoAH0gNCAPyJxz4BlCFFxWNE1OPTgk5TthT...',
                    'Expiration': '2023-01-01T12:00:00Z'
                }
            }
            mock_sts_client.get_session_token.return_value = mock_response

            result = client.get_session_token()
            assert result == mock_response
            mock_sts_client.get_session_token.assert_called_once_with(DurationSeconds=3600)

def test_get_session_token_no_credentials():
    """Test get_session_token with no credentials"""
    with patch.dict(os.environ, {'AWS_REGION': 'us-west-2'}):
        with patch('boto3.Session') as mock_session:
            mock_sess = MagicMock()
            mock_sts_client = MagicMock()
            mock_session.return_value = mock_sess
            mock_sess.client.return_value = mock_sts_client

            client = STSClient()
            mock_sts_client.get_session_token.side_effect = NoCredentialsError()

            with pytest.raises(InternalServerException) as exc_info:
                client.get_session_token()
            assert "AWS credentials not configured" in str(exc_info.value)

def test_get_session_token_client_error():
    """Test get_session_token with client error"""
    with patch.dict(os.environ, {'AWS_REGION': 'us-west-2'}):
        with patch('boto3.Session') as mock_session:
            mock_sess = MagicMock()
            mock_sts_client = MagicMock()
            mock_session.return_value = mock_sess
            mock_sess.client.return_value = mock_sts_client

            client = STSClient()
            mock_sts_client.get_session_token.side_effect = ClientError(
                {'Error': {'Code': 'AccessDenied', 'Message': 'Access denied'}},
                'GetSessionToken'
            )

            with pytest.raises(InternalServerException) as exc_info:
                client.get_session_token()
            assert "AWS STS get session token error" in str(exc_info.value)

def test_get_client():
    """Test get_client method"""
    with patch.dict(os.environ, {'AWS_REGION': 'us-west-2'}):
        with patch('boto3.Session') as mock_session:
            mock_sess = MagicMock()
            mock_s3_client = Mock()
            mock_session.return_value = mock_sess
            mock_sess.client.return_value = mock_s3_client

            client = STSClient()

            result = client.get_client('s3')
            assert result == mock_s3_client
            # The client method is called twice: once for 'sts' during init, once for 's3'
            assert mock_sess.client.call_count == 2
            mock_sess.client.assert_any_call('sts')
            mock_sess.client.assert_any_call('s3')

def test_get_resource():
    """Test get_resource method"""
    with patch.dict(os.environ, {'AWS_REGION': 'us-west-2'}):
        with patch('boto3.Session') as mock_session:
            mock_sess = MagicMock()
            mock_dynamodb_resource = Mock()
            mock_session.return_value = mock_sess
            mock_sess.resource.return_value = mock_dynamodb_resource

            client = STSClient()

            result = client.get_resource('dynamodb')
            assert result == mock_dynamodb_resource
            mock_sess.resource.assert_called_once_with('dynamodb')