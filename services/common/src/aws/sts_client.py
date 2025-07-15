"""
AWS STS Client for assuming roles
Handles both local development and Kubernetes environments
"""
import os
import boto3
import logging
from typing import Optional
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class STSClient:
    """AWS STS client for role assumption"""

    def __init__(self, role_arn: Optional[str] = None):
        self.role_arn = role_arn or os.getenv('AWS_ROLE_ARN')
        self.session = None

    def get_credentials(self):
        """Get AWS credentials via role assumption or local config"""

        # Check if we're in Kubernetes with IRSA
        if os.getenv('AWS_WEB_IDENTITY_TOKEN_FILE'):
            logger.info("Using IRSA credentials from Kubernetes")
            region = os.getenv('AWS_REGION')
            if not region:
                raise ValueError("AWS_REGION environment variable is required")
            return boto3.Session(region_name=region)

        # Check if we have a role to assume
        if self.role_arn:
            logger.info(f"Assuming role: {self.role_arn}")
            return self._assume_role()

        # Fallback to local credentials
        logger.info("Using local AWS credentials")
        region = os.getenv('AWS_REGION')
        if not region:
            raise ValueError("AWS_REGION environment variable is required")
        return boto3.Session(region_name=region)

    def _assume_role(self):
        """Assume the specified IAM role"""
        try:
            # Get region from environment
            region = os.getenv('AWS_REGION')
            if not region:
                raise ValueError("AWS_REGION environment variable is required")
            sts_client = boto3.client('sts', region_name=region)

            # Assume role with session name
            session_name = f"order-processor-{os.getenv('ENVIRONMENT', 'dev')}"

            response = sts_client.assume_role(
                RoleArn=self.role_arn,
                RoleSessionName=session_name
            )

            # Create session with temporary credentials and region
            self.session = boto3.Session(
                aws_access_key_id=response['Credentials']['AccessKeyId'],
                aws_secret_access_key=response['Credentials']['SecretAccessKey'],
                aws_session_token=response['Credentials']['SessionToken'],
                region_name=region
            )

            logger.info(f"Successfully assumed role: {self.role_arn} in region: {region}")
            return self.session

        except ClientError as e:
            logger.error(f"Failed to assume role: {e}")
            # Fallback to local credentials with region
            region = os.getenv('AWS_REGION')
            if not region:
                raise ValueError("AWS_REGION environment variable is required")
            return boto3.Session(region_name=region)

    def get_client(self, service_name: str):
        """Get AWS client for specified service"""
        session = self.get_credentials()
        return session.client(service_name)

    def get_resource(self, service_name: str):
        """Get AWS resource for specified service"""
        session = self.get_credentials()
        return session.resource(service_name)