#!/usr/bin/env python3
# File: terraform/infrastructure-tests/helpers/aws_helpers.py
# AWS operation utilities
# AWSResourceManager for complex AWS operations
# VPC resource discovery and validation
# ECS cluster comprehensive info
# S3 security configuration checking
# Resource tagging validation

import boto3
import time
from typing import Dict, Any, List, Optional
from botocore.exceptions import ClientError, NoCredentialsError
import json

class AWSResourceManager:
    """Advanced AWS resource management utilities"""

    def __init__(self, region: str = "us-west-2"):
        self.region = region
        self.session = boto3.Session(region_name=region)

    def get_client(self, service_name: str):
        """Get AWS service client with error handling"""
        try:
            return self.session.client(service_name)
        except NoCredentialsError:
            raise RuntimeError(f"AWS credentials not configured for {service_name}")

    def get_resource(self, service_name: str):
        """Get AWS service resource with error handling"""
        try:
            return self.session.resource(service_name)
        except NoCredentialsError:
            raise RuntimeError(f"AWS credentials not configured for {service_name}")

    def wait_for_stack_status(self, stack_name: str, target_status: str,
                             timeout: int = 1800) -> bool:
        """Wait for CloudFormation stack to reach target status"""
        cf = self.get_client('cloudformation')
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                response = cf.describe_stacks(StackName=stack_name)
                stacks = response['Stacks']

                if not stacks:
                    return False

                current_status = stacks[0]['StackStatus']

                if current_status == target_status:
                    return True

                if current_status.endswith('_FAILED'):
                    raise RuntimeError(f"Stack {stack_name} failed with status: {current_status}")

                time.sleep(30)  # Wait 30 seconds between checks

            except ClientError as e:
                if e.response['Error']['Code'] == 'ValidationError':
                    # Stack doesn't exist
                    return target_status == 'DELETE_COMPLETE'
                raise

        return False

    def get_vpc_resources(self, vpc_id: str) -> Dict[str, List]:
        """Get all resources associated with a VPC"""
        ec2 = self.get_client('ec2')
        resources = {
            'subnets': [],
            'security_groups': [],
            'route_tables': [],
            'internet_gateways': [],
            'nat_gateways': [],
            'instances': []
        }

        try:
            # Get subnets
            response = ec2.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
            resources['subnets'] = response['Subnets']

            # Get security groups
            response = ec2.describe_security_groups(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
            resources['security_groups'] = response['SecurityGroups']

            # Get route tables
            response = ec2.describe_route_tables(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
            resources['route_tables'] = response['RouteTables']

            # Get internet gateways
            response = ec2.describe_internet_gateways(
                Filters=[{'Name': 'attachment.vpc-id', 'Values': [vpc_id]}]
            )
            resources['internet_gateways'] = response['InternetGateways']

            # Get NAT gateways
            response = ec2.describe_nat_gateways(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
            resources['nat_gateways'] = response['NatGateways']

            # Get instances
            response = ec2.describe_instances(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
            instances = []
            for reservation in response['Reservations']:
                instances.extend(reservation['Instances'])
            resources['instances'] = instances

        except ClientError as e:
            print(f"Error getting VPC resources: {e}")

        return resources

    def get_ecs_cluster_info(self, cluster_name: str) -> Dict[str, Any]:
        """Get comprehensive ECS cluster information"""
        ecs = self.get_client('ecs')

        try:
            # Get cluster details
            cluster_response = ecs.describe_clusters(clusters=[cluster_name], include=['TAGS'])

            if not cluster_response['clusters']:
                return {}

            cluster = cluster_response['clusters'][0]

            # Get services
            services_response = ecs.list_services(cluster=cluster_name)
            service_arns = services_response['serviceArns']

            services = []
            if service_arns:
                services_detail = ecs.describe_services(cluster=cluster_name, services=service_arns)
                services = services_detail['services']

            # Get tasks
            tasks_response = ecs.list_tasks(cluster=cluster_name)
            task_arns = tasks_response['taskArns']

            tasks = []
            if task_arns:
                tasks_detail = ecs.describe_tasks(cluster=cluster_name, tasks=task_arns)
                tasks = tasks_detail['tasks']

            return {
                'cluster': cluster,
                'services': services,
                'tasks': tasks,
                'service_count': len(services),
                'task_count': len(tasks)
            }

        except ClientError as e:
            print(f"Error getting ECS cluster info: {e}")
            return {}

    def check_s3_bucket_policy(self, bucket_name: str) -> Dict[str, Any]:
        """Check S3 bucket security configuration"""
        s3 = self.get_client('s3')
        security_config = {}

        try:
            # Check bucket policy
            try:
                policy_response = s3.get_bucket_policy(Bucket=bucket_name)
                security_config['bucket_policy'] = json.loads(policy_response['Policy'])
            except ClientError as e:
                if e.response['Error']['Code'] != 'NoSuchBucketPolicy':
                    raise
                security_config['bucket_policy'] = None

            # Check bucket ACL
            acl_response = s3.get_bucket_acl(Bucket=bucket_name)
            security_config['acl'] = acl_response

            # Check public access block
            try:
                pab_response = s3.get_public_access_block(Bucket=bucket_name)
                security_config['public_access_block'] = pab_response['PublicAccessBlockConfiguration']
            except ClientError as e:
                if e.response['Error']['Code'] != 'NoSuchPublicAccessBlockConfiguration':
                    raise
                security_config['public_access_block'] = None

            # Check encryption
            try:
                encryption_response = s3.get_bucket_encryption(Bucket=bucket_name)
                security_config['encryption'] = encryption_response['ServerSideEncryptionConfiguration']
            except ClientError as e:
                if e.response['Error']['Code'] != 'ServerSideEncryptionConfigurationNotFoundError':
                    raise
                security_config['encryption'] = None

            # Check versioning
            versioning_response = s3.get_bucket_versioning(Bucket=bucket_name)
            security_config['versioning'] = versioning_response

        except ClientError as e:
            print(f"Error checking S3 bucket security: {e}")

        return security_config

    def get_resource_tags(self, resource_arn: str) -> Dict[str, str]:
        """Get tags for any AWS resource"""
        try:
            # Determine service from ARN
            service = resource_arn.split(':')[2]

            if service == 'ec2':
                ec2 = self.get_client('ec2')
                # Extract resource ID from ARN
                resource_id = resource_arn.split('/')[-1]
                response = ec2.describe_tags(Filters=[{'Name': 'resource-id', 'Values': [resource_id]}])
                return {tag['Key']: tag['Value'] for tag in response['Tags']}

            elif service == 's3':
                s3 = self.get_client('s3')
                bucket_name = resource_arn.split(':')[-1]
                response = s3.get_bucket_tagging(Bucket=bucket_name)
                return {tag['Key']: tag['Value'] for tag in response['TagSet']}

            elif service == 'ecs':
                ecs = self.get_client('ecs')
                response = ecs.list_tags_for_resource(resourceArn=resource_arn)
                return {tag['key']: tag['value'] for tag in response['tags']}

            # Add more services as needed

        except ClientError:
            # Resource might not support tagging or tags might not exist
            pass

        return {}
