import os
import pytest
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError

import sys
import importlib.util

# Dynamically import the STSClient class
spec = importlib.util.spec_from_file_location(
    "sts_client",
    os.path.join(os.path.dirname(__file__), '../../src/aws/sts_client.py')
)
sts_client_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sts_client_module)
STSClient = sts_client_module.STSClient

@pytest.fixture(autouse=True)
def clear_env(monkeypatch):
    monkeypatch.delenv('AWS_WEB_IDENTITY_TOKEN_FILE', raising=False)
    monkeypatch.delenv('AWS_ROLE_ARN', raising=False)
    monkeypatch.delenv('AWS_REGION', raising=False)
    monkeypatch.delenv('ENVIRONMENT', raising=False)


def test_get_credentials_irsa(monkeypatch):
    monkeypatch.setenv('AWS_WEB_IDENTITY_TOKEN_FILE', '/tmp/token')
    monkeypatch.setenv('AWS_REGION', 'us-west-2')
    with patch('boto3.Session') as mock_session:
        client = STSClient()
        session = client.get_credentials()
        mock_session.assert_called_once_with(region_name='us-west-2')
        assert session == mock_session.return_value


def test_get_credentials_assume_role(monkeypatch):
    monkeypatch.setenv('AWS_ROLE_ARN', 'arn:aws:iam::123456789012:role/test-role')
    monkeypatch.setenv('AWS_REGION', 'us-west-2')
    monkeypatch.setenv('ENVIRONMENT', 'testenv')
    with patch('boto3.client') as mock_boto_client, \
         patch('boto3.Session') as mock_boto_session:
        mock_sts = MagicMock()
        mock_boto_client.return_value = mock_sts
        mock_sts.assume_role.return_value = {
            'Credentials': {
                'AccessKeyId': 'AKIA...',
                'SecretAccessKey': 'SECRET',
                'SessionToken': 'TOKEN'
            }
        }
        client = STSClient()
        session = client.get_credentials()
        mock_boto_client.assert_called_once_with('sts', region_name='us-west-2')
        mock_sts.assume_role.assert_called_once()
        mock_boto_session.assert_called_with(
            aws_access_key_id='AKIA...',
            aws_secret_access_key='SECRET',
            aws_session_token='TOKEN',
            region_name='us-west-2'
        )
        assert session == mock_boto_session.return_value


def test_get_credentials_local(monkeypatch):
    monkeypatch.setenv('AWS_REGION', 'us-west-2')
    with patch('boto3.Session') as mock_session:
        client = STSClient()
        session = client.get_credentials()
        mock_session.assert_called_once_with(region_name='us-west-2')
        assert session == mock_session.return_value


def test_get_credentials_missing_region(monkeypatch):
    # No AWS_REGION set
    with pytest.raises(ValueError):
        client = STSClient()
        client.get_credentials()


def test_assume_role_client_error(monkeypatch):
    monkeypatch.setenv('AWS_ROLE_ARN', 'arn:aws:iam::123456789012:role/test-role')
    monkeypatch.setenv('AWS_REGION', 'us-west-2')
    with patch('boto3.client') as mock_boto_client, \
         patch('boto3.Session') as mock_boto_session:
        mock_sts = MagicMock()
        mock_boto_client.return_value = mock_sts
        mock_sts.assume_role.side_effect = ClientError({'Error': {}}, 'AssumeRole')
        client = STSClient()
        session = client.get_credentials()
        # Should fallback to local credentials
        mock_boto_session.assert_called_with(region_name='us-west-2')
        assert session == mock_boto_session.return_value


def test_get_client_and_resource(monkeypatch):
    monkeypatch.setenv('AWS_REGION', 'us-west-2')
    with patch('boto3.Session') as mock_session:
        mock_sess = MagicMock()
        mock_session.return_value = mock_sess
        client = STSClient()
        aws_client = client.get_client('s3')
        aws_resource = client.get_resource('dynamodb')
        mock_sess.client.assert_called_with('s3')
        mock_sess.resource.assert_called_with('dynamodb')
        assert aws_client == mock_sess.client.return_value
        assert aws_resource == mock_sess.resource.return_value