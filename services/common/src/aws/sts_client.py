"""
AWS STS Client for assuming roles
Handles both local development and Kubernetes environments
"""
import os
from typing import Any, Dict, Optional

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from ..exceptions import CNOPInternalServerException
from ..shared.logging import BaseLogger, LogAction, LoggerName

logger = BaseLogger(LoggerName.AUDIT, log_to_file=True)

class STSClient:
    """AWS STS client for role assumption"""

    def __init__(self):
        """Initialize STS client"""
        self.region = os.getenv('AWS_REGION')
        if not self.region:
            raise CNOPInternalServerException("AWS_REGION environment variable is required")

        self.session = boto3.Session(region_name=self.region)
        self.sts_client = self.session.client('sts')

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
            logger.error(
                action=LogAction.ERROR,
                message="No AWS credentials found"
            )
            raise CNOPInternalServerException("AWS credentials not configured")
        except ClientError as e:
            logger.error(
                action=LogAction.ERROR,
                message=f"AWS STS assume role error: {e}"
            )
            raise CNOPInternalServerException(f"AWS STS assume role error: {e}")
        raise CNOPInternalServerException(f"AWS STS get session token error: {e}")

    def get_client(self, service_name: str):
        """Get AWS client for specified service"""
        return self.session.client(service_name)
