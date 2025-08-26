"""
AWS STS Client for assuming roles
Handles both local development and Kubernetes environments
"""
import os
import boto3
import logging
from typing import Optional, Dict, Any
from botocore.exceptions import ClientError, NoCredentialsError

from ..exceptions import CNOPInternalServerException

logger = logging.getLogger(__name__)

class STSClient:
    """AWS STS client for role assumption"""

    def __init__(self):
        """Initialize STS client"""
        self.region = os.getenv('AWS_REGION')
        if not self.region:
            raise CNOPInternalServerException("AWS_REGION environment variable is required")

        self.session = boto3.Session(region_name=self.region)
        self.sts_client = self.session.client('sts')

    def get_caller_identity(self) -> Dict[str, Any]:
        """Get current AWS caller identity"""
        try:
            if not self.region:
                raise CNOPInternalServerException("AWS_REGION environment variable is required")

            response = self.sts_client.get_caller_identity()
            return response
        except NoCredentialsError:
            logger.error("No AWS credentials found")
            raise CNOPInternalServerException("AWS credentials not configured")
        except ClientError as e:
            logger.error(f"AWS STS error: {e}")
            raise CNOPInternalServerException(f"AWS STS error: {e}")

    def assume_role(self, role_arn: str, role_session_name: str,
                   duration_seconds: int = 3600) -> Dict[str, Any]:
        """Assume an IAM role"""
        try:
            if not self.region:
                raise CNOPInternalServerException("AWS_REGION environment variable is required")

            response = self.sts_client.assume_role(
                RoleArn=role_arn,
                RoleSessionName=role_session_name,
                DurationSeconds=duration_seconds
            )
            return response
        except NoCredentialsError:
            logger.error("No AWS credentials found")
            raise CNOPInternalServerException("AWS credentials not configured")
        except ClientError as e:
            logger.error(f"AWS STS assume role error: {e}")
            raise CNOPInternalServerException(f"AWS STS assume role error: {e}")

    def get_session_token(self, duration_seconds: int = 3600) -> Dict[str, Any]:
        """Get temporary session token"""
        try:
            if not self.region:
                raise CNOPInternalServerException("AWS_REGION environment variable is required")

            response = self.sts_client.get_session_token(
                DurationSeconds=duration_seconds
            )
            return response
        except NoCredentialsError:
            logger.error("No AWS credentials found")
            raise CNOPInternalServerException("AWS credentials not configured")
        except ClientError as e:
            logger.error(f"AWS STS get session token error: {e}")
            raise CNOPInternalServerException(f"AWS STS get session token error: {e}")

    def get_client(self, service_name: str):
        """Get AWS client for specified service"""
        return self.session.client(service_name)

    def get_resource(self, service_name: str):
        """Get AWS resource for specified service"""
        return self.session.resource(service_name)