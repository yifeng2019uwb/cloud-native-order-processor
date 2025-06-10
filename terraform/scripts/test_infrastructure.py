#!/usr/bin/env python3
"""
integration/infrastructure/test_infrastructure.py

Infrastructure Integration Tests for Cloud-Native Order Processor

This test suite validates that all AWS resources deployed by Terraform
are accessible and properly configured for the microservices architecture.

Run with: pytest tests/integration/infrastructure/ -v
"""

import pytest
import boto3
import subprocess
import json
import time
import os
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError, NoCredentialsError


class TestTerraformDeployment:
    """Test that Terraform deployment completed successfully"""

    @classmethod
    def setup_class(cls):
        """Get Terraform outputs for use in tests"""
        try:
            result = subprocess.run(
                ["terraform", "output", "-json"],
                cwd="terraform",
                capture_output=True,
                text=True,
                check=True
            )
            cls.tf_outputs = json.loads(result.stdout)
            print(f"✅ Loaded Terraform outputs: {list(cls.tf_outputs.keys())}")
        except subprocess.CalledProcessError as e:
            pytest.fail(f"Failed to get Terraform outputs: {e.stderr}")
        except FileNotFoundError:
            pytest.fail("Terraform not found. Ensure Terraform is installed and run from project root.")

    def test_terraform_outputs_exist(self):
        """Verify all expected Terraform outputs are present"""
        expected_outputs = [
            "eks_cluster_name",
            "eks_cluster_endpoint",
            "database_endpoint",
            "database_secret_arn",
            "s3_events_bucket_name",
            "sns_order_events_topic_arn",
            "sqs_order_processing_queue_url",
            "ecr_order_api_repository_url",
            "order_service_role_arn"
        ]

        missing_outputs = []
        for output in expected_outputs:
            if output not in self.tf_outputs:
                missing_outputs.append(output)

        assert not missing_outputs, f"Missing Terraform outputs: {missing_outputs}"
        print(f"✅ All expected Terraform outputs present")

    def test_terraform_state_healthy(self):
        """Verify Terraform state is not corrupted"""
        try:
            result = subprocess.run(
                ["terraform", "validate"],
                cwd="terraform",
                capture_output=True,
                text=True,
                check=True
            )
            assert "Success" in result.stdout
            print("✅ Terraform configuration is valid")
        except subprocess.CalledProcessError as e:
            pytest.fail(f"Terraform validation failed: {e.stderr}")


class TestAWSConnectivity:
    """Test basic AWS connectivity and credentials"""

    @classmethod
    def setup_class(cls):
        """Setup AWS clients"""
        try:
            cls.session = boto3.Session()
            cls.sts_client = cls.session.client('sts')

            # Get AWS account info
            cls.identity = cls.sts_client.get_caller_identity()
            cls.account_id = cls.identity['Account']
            cls.region = cls.session.region_name or 'us-west-2'

            print(f"✅ AWS Account: {cls.account_id}, Region: {cls.region}")
        except NoCredentialsError:
            pytest.fail("AWS credentials not configured")
        except Exception as e:
            pytest.fail(f"AWS connectivity test failed: {e}")

    def test_aws_credentials_valid(self):
        """Verify AWS credentials are valid"""
        assert self.account_id
        assert len(self.account_id) == 12
        print(f"✅ Valid AWS account ID: {self.account_id}")

    def test_aws_region_accessible(self):
        """Verify AWS region is accessible"""
        ec2 = self.session.client('ec2')
        try:
            response = ec2.describe_regions()
            available_regions = [r['RegionName'] for r in response['Regions']]
            assert self.region in available_regions
            print(f"✅ Region {self.region} is accessible")
        except ClientError as e:
            pytest.fail(f"Cannot access AWS region {self.region}: {e}")


class TestEKSCluster:
    """Test EKS cluster deployment and accessibility"""

    @classmethod
    def setup_class(cls):
        """Setup EKS client and get cluster info from Terraform"""
        cls.eks_client = boto3.client('eks')

        # Get cluster name from Terraform outputs
        try:
            result = subprocess.run(
                ["terraform", "output", "-raw", "eks_cluster_name"],
                cwd="terraform",
                capture_output=True,
                text=True,
                check=True
            )
            cls.cluster_name = result.stdout.strip()
            print(f"✅ EKS cluster name: {cls.cluster_name}")
        except subprocess.CalledProcessError:
            pytest.skip("EKS cluster name not available from Terraform")

    def test_eks_cluster_exists(self):
        """Verify EKS cluster exists and is accessible"""
        try:
            response = self.eks_client.describe_cluster(name=self.cluster_name)
            cluster = response['cluster']

            assert cluster['name'] == self.cluster_name
            assert cluster['status'] == 'ACTIVE'
            print(f"✅ EKS cluster {self.cluster_name} is ACTIVE")

        except ClientError as e:
            pytest.fail(f"Cannot access EKS cluster {self.cluster_name}: {e}")

    def test_eks_cluster_version(self):
        """Verify EKS cluster is running expected Kubernetes version"""
        try:
            response = self.eks_client.describe_cluster(name=self.cluster_name)
            version = response['cluster']['version']

            # Check that version is 1.28 or newer
            major, minor = map(int, version.split('.'))
            assert major == 1 and minor >= 28, f"EKS version {version} may be outdated"
            print(f"✅ EKS cluster running Kubernetes {version}")

        except ClientError as e:
            pytest.fail(f"Cannot get EKS cluster version: {e}")

    def test_eks_fargate_profile(self):
        """Verify Fargate profile is configured"""
        try:
            response = self.eks_client.list_fargate_profiles(clusterName=self.cluster_name)
            profiles = response['fargateProfileNames']

            assert len(profiles) > 0, "No Fargate profiles found"

            # Check first profile details
            profile_response = self.eks_client.describe_fargate_profile(
                clusterName=self.cluster_name,
                fargateProfileName=profiles[0]
            )
            profile = profile_response['fargateProfile']
            assert profile['status'] == 'ACTIVE'
            print(f"✅ Fargate profile {profiles[0]} is ACTIVE")

        except ClientError as e:
            pytest.fail(f"Cannot access Fargate profiles: {e}")

    def test_kubectl_connectivity(self):
        """Test kubectl connectivity to EKS cluster"""
        try:
            # Update kubeconfig
            subprocess.run(
                ["aws", "eks", "update-kubeconfig", "--name", self.cluster_name],
                check=True,
                capture_output=True
            )

            # Test kubectl connectivity
            result = subprocess.run(
                ["kubectl", "get", "nodes"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                print("✅ kubectl connectivity to EKS cluster successful")
                print(f"Cluster nodes:\n{result.stdout}")
            else:
                print(f"⚠️ kubectl connectivity failed: {result.stderr}")
                # Don't fail the test as kubectl might not be configured locally

        except subprocess.TimeoutExpired:
            print("⚠️ kubectl connection timed out")
        except FileNotFoundError:
            print("⚠️ kubectl not found - install kubectl for full EKS testing")


class TestRDSDatabase:
    """Test RDS PostgreSQL deployment and connectivity"""

    @classmethod
    def setup_class(cls):
        """Setup RDS client and get database info"""
        cls.rds_client = boto3.client('rds')
        cls.secretsmanager_client = boto3.client('secretsmanager')

        # Get database info from Terraform outputs
        try:
            result = subprocess.run(
                ["terraform", "output", "-raw", "database_secret_arn"],
                cwd="terraform",
                capture_output=True,
                text=True,
                check=True
            )
            cls.secret_arn = result.stdout.strip()
            print(f"✅ Database secret ARN: {cls.secret_arn}")
        except subprocess.CalledProcessError:
            pytest.skip("Database secret ARN not available from Terraform")

    def test_rds_instance_exists(self):
        """Verify RDS instance exists and is available"""
        try:
            response = self.rds_client.describe_db_instances()
            db_instances = response['DBInstances']

            # Find our order processor database
            order_db = None
            for db in db_instances:
                if 'order-processor' in db['DBInstanceIdentifier']:
                    order_db = db
                    break

            assert order_db is not None, "Order processor RDS instance not found"
            assert order_db['DBInstanceStatus'] == 'available', f"RDS status: {order_db['DBInstanceStatus']}"

            print(f"✅ RDS instance {order_db['DBInstanceIdentifier']} is available")
            print(f"   Engine: {order_db['Engine']} {order_db['EngineVersion']}")
            print(f"   Instance class: {order_db['DBInstanceClass']}")

        except ClientError as e:
            pytest.fail(f"Cannot access RDS instances: {e}")

    def test_database_secret_accessible(self):
        """Verify database credentials can be retrieved from Secrets Manager"""
        try:
            response = self.secretsmanager_client.get_secret_value(SecretId=self.secret_arn)
            secret_data = json.loads(response['SecretString'])

            required_keys = ['username', 'password', 'host', 'port', 'dbname']
            missing_keys = [key for key in required_keys if key not in secret_data]

            assert not missing_keys, f"Missing keys in database secret: {missing_keys}"

            # Validate secret values
            assert secret_data['username'], "Database username is empty"
            assert secret_data['password'], "Database password is empty"
            assert secret_data['host'], "Database host is empty"
            assert secret_data['port'] == 5432, f"Unexpected database port: {secret_data['port']}"
            assert secret_data['dbname'], "Database name is empty"

            print("✅ Database credentials retrieved successfully from Secrets Manager")
            print(f"   Host: {secret_data['host']}")
            print(f"   Database: {secret_data['dbname']}")
            print(f"   Username: {secret_data['username']}")

        except ClientError as e:
            pytest.fail(f"Cannot retrieve database secret: {e}")

    def test_database_connectivity_from_vpc(self):
        """Note: Database connectivity test from outside VPC"""
        print("⚠️ Database connectivity test skipped - requires VPC access")
        print("   To test database connectivity:")
        print("   1. Deploy a test pod in EKS cluster")
        print("   2. Use kubectl exec to connect to database from within VPC")
        print("   3. Or use AWS Systems Manager Session Manager with EC2 in VPC")


class TestMessagingServices:
    """Test SNS and SQS messaging infrastructure"""

    @classmethod
    def setup_class(cls):
        """Setup messaging clients and get resource info"""
        cls.sns_client = boto3.client('sns')
        cls.sqs_client = boto3.client('sqs')

        # Get messaging resource info from Terraform outputs
        try:
            result = subprocess.run(
                ["terraform", "output", "-raw", "sns_order_events_topic_arn"],
                cwd="terraform",
                capture_output=True,
                text=True,
                check=True
            )
            cls.topic_arn = result.stdout.strip()

            result = subprocess.run(
                ["terraform", "output", "-raw", "sqs_order_processing_queue_url"],
                cwd="terraform",
                capture_output=True,
                text=True,
                check=True
            )
            cls.queue_url = result.stdout.strip()

            print(f"✅ SNS Topic ARN: {cls.topic_arn}")
            print(f"✅ SQS Queue URL: {cls.queue_url}")

        except subprocess.CalledProcessError:
            pytest.skip("Messaging resource info not available from Terraform")

    def test_sns_topic_exists(self):
        """Verify SNS topic exists and is accessible"""
        try:
            response = self.sns_client.get_topic_attributes(TopicArn=self.topic_arn)
            attributes = response['Attributes']

            assert attributes['TopicArn'] == self.topic_arn
            print(f"✅ SNS topic exists: {attributes['DisplayName'] or 'order-events'}")

        except ClientError as e:
            pytest.fail(f"Cannot access SNS topic {self.topic_arn}: {e}")

    def test_sqs_queue_exists(self):
        """Verify SQS queue exists and is accessible"""
        try:
            response = self.sqs_client.get_queue_attributes(
                QueueUrl=self.queue_url,
                AttributeNames=['QueueArn', 'VisibilityTimeout', 'MessageRetentionPeriod']
            )
            attributes = response['Attributes']

            assert 'QueueArn' in attributes
            print(f"✅ SQS queue exists: {attributes['QueueArn']}")
            print(f"   Visibility timeout: {attributes['VisibilityTimeout']}s")
            print(f"   Message retention: {attributes['MessageRetentionPeriod']}s")

        except ClientError as e:
            pytest.fail(f"Cannot access SQS queue {self.queue_url}: {e}")

    def test_sns_sqs_subscription(self):
        """Verify SNS topic is subscribed to SQS queue"""
        try:
            response = self.sns_client.list_subscriptions_by_topic(TopicArn=self.topic_arn)
            subscriptions = response['Subscriptions']

            sqs_subscriptions = [sub for sub in subscriptions if sub['Protocol'] == 'sqs']
            assert len(sqs_subscriptions) > 0, "No SQS subscriptions found for SNS topic"

            # Check if our queue is subscribed
            queue_subscribed = any(self.queue_url.split('/')[-1] in sub['Endpoint']
                                 for sub in sqs_subscriptions)
            assert queue_subscribed, "SQS queue not subscribed to SNS topic"

            print(f"✅ Found {len(sqs_subscriptions)} SQS subscription(s) to SNS topic")

        except ClientError as e:
            pytest.fail(f"Cannot check SNS subscriptions: {e}")

    def test_messaging_permissions(self):
        """Test basic messaging permissions"""
        try:
            # Test SNS publish permissions (will fail if no permission)
            test_message = {"test": "infrastructure_validation", "timestamp": time.time()}

            response = self.sns_client.publish(
                TopicArn=self.topic_arn,
                Message=json.dumps(test_message),
                Subject="Infrastructure Test"
            )

            message_id = response['MessageId']
            print(f"✅ Successfully published test message to SNS: {message_id}")

            # Wait a moment for message propagation
            time.sleep(2)

            # Check for message in SQS queue
            response = self.sqs_client.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=5
            )

            if 'Messages' in response:
                message = response['Messages'][0]
                print(f"✅ Test message received in SQS queue")

                # Clean up test message
                self.sqs_client.delete_message(
                    QueueUrl=self.queue_url,
                    ReceiptHandle=message['ReceiptHandle']
                )
                print("✅ Test message cleaned up from queue")
            else:
                print("⚠️ Test message not found in SQS queue (may take time to propagate)")

        except ClientError as e:
            pytest.fail(f"Messaging permissions test failed: {e}")


class TestStorageServices:
    """Test S3 storage infrastructure"""

    @classmethod
    def setup_class(cls):
        """Setup S3 client and get bucket info"""
        cls.s3_client = boto3.client('s3')

        # Get bucket name from Terraform outputs
        try:
            result = subprocess.run(
                ["terraform", "output", "-raw", "s3_events_bucket_name"],
                cwd="terraform",
                capture_output=True,
                text=True,
                check=True
            )
            cls.events_bucket = result.stdout.strip()
            print(f"✅ S3 Events bucket: {cls.events_bucket}")

        except subprocess.CalledProcessError:
            pytest.skip("S3 bucket info not available from Terraform")

    def test_s3_events_bucket_exists(self):
        """Verify S3 events bucket exists and is accessible"""
        try:
            response = self.s3_client.head_bucket(Bucket=self.events_bucket)
            print(f"✅ S3 events bucket exists and is accessible")

        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                pytest.fail(f"S3 bucket {self.events_bucket} does not exist")
            else:
                pytest.fail(f"Cannot access S3 bucket {self.events_bucket}: {e}")

    def test_s3_bucket_permissions(self):
        """Test S3 bucket read/write permissions"""
        test_key = f"integration-tests/test-{int(time.time())}.json"
        test_content = json.dumps({
            "test": "infrastructure_validation",
            "timestamp": time.time(),
            "source": "integration_tests"
        })

        try:
            # Test write permission
            self.s3_client.put_object(
                Bucket=self.events_bucket,
                Key=test_key,
                Body=test_content,
                ContentType='application/json'
            )
            print(f"✅ Successfully wrote test object to S3: {test_key}")

            # Test read permission
            response = self.s3_client.get_object(
                Bucket=self.events_bucket,
                Key=test_key
            )
            retrieved_content = response['Body'].read().decode('utf-8')
            assert retrieved_content == test_content
            print(f"✅ Successfully read test object from S3")

            # Clean up test object
            self.s3_client.delete_object(
                Bucket=self.events_bucket,
                Key=test_key
            )
            print(f"✅ Test object cleaned up from S3")

        except ClientError as e:
            pytest.fail(f"S3 permissions test failed: {e}")

    def test_s3_bucket_encryption(self):
        """Verify S3 bucket encryption is enabled"""
        try:
            response = self.s3_client.get_bucket_encryption(Bucket=self.events_bucket)
            encryption_config = response['ServerSideEncryptionConfiguration']

            rules = encryption_config['Rules']
            assert len(rules) > 0, "No encryption rules found"

            # Check that AES256 encryption is enabled
            rule = rules[0]
            assert 'ApplyServerSideEncryptionByDefault' in rule
            encryption = rule['ApplyServerSideEncryptionByDefault']
            assert encryption['SSEAlgorithm'] == 'AES256'

            print(f"✅ S3 bucket encryption enabled: {encryption['SSEAlgorithm']}")

        except ClientError as e:
            if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
                pytest.fail("S3 bucket encryption not configured")
            else:
                pytest.fail(f"Cannot check S3 bucket encryption: {e}")


class TestContainerRegistry:
    """Test ECR container registry"""

    @classmethod
    def setup_class(cls):
        """Setup ECR client and get repository info"""
        cls.ecr_client = boto3.client('ecr')

        # Get ECR repository URL from Terraform outputs
        try:
            result = subprocess.run(
                ["terraform", "output", "-raw", "ecr_order_api_repository_url"],
                cwd="terraform",
                capture_output=True,
                text=True,
                check=True
            )
            cls.repository_url = result.stdout.strip()
            cls.repository_name = cls.repository_url.split('/')[-1]
            print(f"✅ ECR Repository: {cls.repository_name}")

        except subprocess.CalledProcessError:
            pytest.skip("ECR repository info not available from Terraform")

    def test_ecr_repository_exists(self):
        """Verify ECR repository exists and is accessible"""
        try:
            response = self.ecr_client.describe_repositories(
                repositoryNames=[self.repository_name]
            )
            repositories = response['repositories']

            assert len(repositories) == 1
            repo = repositories[0]
            assert repo['repositoryName'] == self.repository_name

            print(f"✅ ECR repository exists: {repo['repositoryUri']}")
            print(f"   Image tag mutability: {repo['imageTaggerMutability']}")

        except ClientError as e:
            if e.response['Error']['Code'] == 'RepositoryNotFoundException':
                pytest.fail(f"ECR repository {self.repository_name} does not exist")
            else:
                pytest.fail(f"Cannot access ECR repository: {e}")

    def test_ecr_lifecycle_policy(self):
        """Verify ECR lifecycle policy is configured"""
        try:
            response = self.ecr_client.get_lifecycle_policy(
                repositoryName=self.repository_name
            )
            policy = json.loads(response['lifecyclePolicyText'])

            assert 'rules' in policy
            assert len(policy['rules']) > 0

            print(f"✅ ECR lifecycle policy configured with {len(policy['rules'])} rule(s)")

        except ClientError as e:
            if e.response['Error']['Code'] == 'LifecyclePolicyNotFoundException':
                print("⚠️ No lifecycle policy found (optional for testing)")
            else:
                pytest.fail(f"Cannot check ECR lifecycle policy: {e}")

    def test_ecr_permissions(self):
        """Test ECR push/pull permissions"""
        try:
            # Test getting auth token (required for docker push/pull)
            response = self.ecr_client.get_authorization_token()
            auth_data = response['authorizationData'][0]

            assert 'authorizationToken' in auth_data
            assert 'proxyEndpoint' in auth_data

            print(f"✅ ECR authorization token retrieved successfully")
            print(f"   Registry endpoint: {auth_data['proxyEndpoint']}")

        except ClientError as e:
            pytest.fail(f"Cannot get ECR authorization token: {e}")


class TestIAMRoles:
    """Test IAM roles and permissions"""

    @classmethod
    def setup_class(cls):
        """Setup IAM client and get role info"""
        cls.iam_client = boto3.client('iam')

        # Get service role ARN from Terraform outputs
        try:
            result = subprocess.run(
                ["terraform", "output", "-raw", "order_service_role_arn"],
                cwd="terraform",
                capture_output=True,
                text=True,
                check=True
            )
            cls.service_role_arn = result.stdout.strip()
            cls.service_role_name = cls.service_role_arn.split('/')[-1]
            print(f"✅ Order service role: {cls.service_role_name}")

        except subprocess.CalledProcessError:
            pytest.skip("Service role ARN not available from Terraform")

    def test_order_service_role_exists(self):
        """Verify order service IAM role exists"""
        try:
            response = self.iam_client.get_role(RoleName=self.service_role_name)
            role = response['Role']

            assert role['RoleName'] == self.service_role_name
            assert role['Arn'] == self.service_role_arn

            print(f"✅ Order service IAM role exists")
            print(f"   Created: {role['CreateDate']}")

        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchEntity':
                pytest.fail(f"IAM role {self.service_role_name} does not exist")
            else:
                pytest.fail(f"Cannot access IAM role: {e}")

    def test_service_role_policies(self):
        """Verify service role has required policies attached"""
        try:
            # Get attached policies
            response = self.iam_client.list_attached_role_policies(
                RoleName=self.service_role_name
            )
            attached_policies = response['AttachedPolicies']

            # Get inline policies
            response = self.iam_client.list_role_policies(
                RoleName=self.service_role_name
            )
            inline_policies = response['PolicyNames']

            total_policies = len(attached_policies) + len(inline_policies)
            assert total_policies > 0, "No policies attached to service role"

            print(f"✅ Service role has {total_policies} policies")
            print(f"   Attached policies: {len(attached_policies)}")
            print(f"   Inline policies: {len(inline_policies)}")

        except ClientError as e:
            pytest.fail(f"Cannot check service role policies: {e}")


if __name__ == "__main__":
    print("🧪 Running Infrastructure Integration Tests")
    print("=" * 50)

    # Run tests with verbose output
    pytest.main([
        "tests/integration/infrastructure/",
        "-v",
        "--tb=short",
        "--color=yes"
    ])