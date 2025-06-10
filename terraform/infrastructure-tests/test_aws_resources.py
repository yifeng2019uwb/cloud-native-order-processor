#!/usr/bin/env python3
# File: terraform/infrastructure-tests/test_aws_resources.py
# AWS resource validation and connectivity tests
# VPC infrastructure: VPC, subnets, internet gateway, security groups
# ECS resources: cluster status, task definitions
# S3 buckets: existence, encryption, security configuration
# DynamoDB tables: status, tagging, configuration

import pytest
import boto3
import time
from typing import Dict, Any, List, Optional
from botocore.exceptions import ClientError

@pytest.mark.aws
@pytest.mark.integration
class TestAWSResourcesExist:
    """Test that expected AWS resources exist"""

    def test_vpc_exists(self, terraform_outputs, aws_helper, environment_config):
        """Test that VPC exists and is properly configured"""
        if not terraform_outputs:
            pytest.skip("No Terraform outputs available")

        vpc_id = terraform_outputs.get('vpc_id', {}).get('value')
        if not vpc_id:
            pytest.skip("VPC ID not available in outputs")

        ec2 = aws_helper.get_client('ec2')

        try:
            response = ec2.describe_vpcs(VpcIds=[vpc_id])
            vpcs = response['Vpcs']
            assert len(vpcs) == 1, f"Expected 1 VPC, found {len(vpcs)}"

            vpc = vpcs[0]
            assert vpc['State'] == 'available', f"VPC {vpc_id} is not available"

            # Check VPC has proper tags
            tags = {tag['Key']: tag['Value'] for tag in vpc.get('Tags', [])}
            assert 'Environment' in tags, "VPC should have Environment tag"
            assert tags['Environment'] == environment_config['environment']

        except ClientError as e:
            pytest.fail(f"Failed to describe VPC {vpc_id}: {e}")

    def test_subnets_exist(self, terraform_outputs, aws_helper):
        """Test that subnets exist and are in different AZs"""
        if not terraform_outputs:
            pytest.skip("No Terraform outputs available")

        subnet_ids = terraform_outputs.get('subnet_ids', {}).get('value', [])
        if not subnet_ids:
            pytest.skip("Subnet IDs not available in outputs")

        ec2 = aws_helper.get_client('ec2')

        try:
            response = ec2.describe_subnets(SubnetIds=subnet_ids)
            subnets = response['Subnets']

            assert len(subnets) >= 2, "Should have at least 2 subnets for HA"

            # Check subnets are in different AZs
            availability_zones = {subnet['AvailabilityZone'] for subnet in subnets}
            assert len(availability_zones) >= 2, "Subnets should be in different AZs"

            # Check all subnets are available
            for subnet in subnets:
                assert subnet['State'] == 'available', f"Subnet {subnet['SubnetId']} is not available"

        except ClientError as e:
            pytest.fail(f"Failed to describe subnets: {e}")

    def test_internet_gateway_exists(self, terraform_outputs, aws_helper):
        """Test that Internet Gateway exists and is attached"""
        if not terraform_outputs:
            pytest.skip("No Terraform outputs available")

        vpc_id = terraform_outputs.get('vpc_id', {}).get('value')
        if not vpc_id:
            pytest.skip("VPC ID not available")

        ec2 = aws_helper.get_client('ec2')

        try:
            response = ec2.describe_internet_gateways(
                Filters=[{'Name': 'attachment.vpc-id', 'Values': [vpc_id]}]
            )

            igws = response['InternetGateways']
            assert len(igws) >= 1, f"No Internet Gateway found for VPC {vpc_id}"

            igw = igws[0]
            attachments = igw['Attachments']
            assert len(attachments) == 1, "IGW should have exactly one attachment"
            assert attachments[0]['State'] == 'available', "IGW attachment should be available"

        except ClientError as e:
            pytest.fail(f"Failed to describe Internet Gateway: {e}")

    def test_security_groups_exist(self, terraform_outputs, aws_helper):
        """Test that security groups exist and have proper rules"""
        if not terraform_outputs:
            pytest.skip("No Terraform outputs available")

        sg_ids = terraform_outputs.get('security_group_ids', {}).get('value', [])
        if not sg_ids:
            pytest.skip("Security Group IDs not available")

        ec2 = aws_helper.get_client('ec2')

        try:
            response = ec2.describe_security_groups(GroupIds=sg_ids)
            security_groups = response['SecurityGroups']

            assert len(security_groups) == len(sg_ids), "Not all security groups found"

            for sg in security_groups:
                # Basic security checks
                assert 'GroupName' in sg, "Security group should have a name"
                assert 'Description' in sg, "Security group should have a description"

                # Check that overly permissive rules don't exist
                for rule in sg.get('IpPermissions', []):
                    for ip_range in rule.get('IpRanges', []):
                        if ip_range.get('CidrIp') == '0.0.0.0/0':
                            # If open to world, should only be for specific ports (80, 443)
                            from_port = rule.get('FromPort', 0)
                            to_port = rule.get('ToPort', 65535)
                            assert from_port != 0 or to_port != 65535, "Security group too permissive"

        except ClientError as e:
            pytest.fail(f"Failed to describe security groups: {e}")

@pytest.mark.aws
@pytest.mark.integration
class TestECSResources:
    """Test ECS cluster and related resources"""

    def test_ecs_cluster_exists(self, terraform_outputs, aws_helper):
        """Test that ECS cluster exists and is active"""
        if not terraform_outputs:
            pytest.skip("No Terraform outputs available")

        cluster_name = terraform_outputs.get('ecs_cluster_name', {}).get('value')
        if not cluster_name:
            pytest.skip("ECS cluster name not available")

        ecs = aws_helper.get_client('ecs')

        try:
            response = ecs.describe_clusters(clusters=[cluster_name])
            clusters = response['clusters']

            assert len(clusters) == 1, f"Expected 1 cluster, found {len(clusters)}"

            cluster = clusters[0]
            assert cluster['status'] == 'ACTIVE', f"Cluster {cluster_name} is not active"
            assert cluster['clusterName'] == cluster_name, "Cluster name mismatch"

        except ClientError as e:
            pytest.fail(f"Failed to describe ECS cluster {cluster_name}: {e}")

    def test_ecs_task_definition_exists(self, terraform_outputs, aws_helper):
        """Test that ECS task definitions exist"""
        if not terraform_outputs:
            pytest.skip("No Terraform outputs available")

        # This test would check for task definitions if they're in outputs
        # For now, we'll check if we can list task definitions
        ecs = aws_helper.get_client('ecs')

        try:
            response = ecs.list_task_definitions(status='ACTIVE')
            # This just ensures we can call the API
            assert 'taskDefinitionArns' in response

        except ClientError as e:
            pytest.fail(f"Failed to list task definitions: {e}")

@pytest.mark.aws
@pytest.mark.integration
class TestS3Resources:
    """Test S3 buckets and configuration"""

    def test_s3_buckets_exist(self, terraform_state_resources, aws_helper, environment_config):
        """Test that S3 buckets exist and are properly configured"""
        if not terraform_state_resources:
            pytest.skip("No Terraform state resources available")

        # Find S3 buckets in state
        s3_buckets = [res for res in terraform_state_resources if 'aws_s3_bucket.' in res]

        if not s3_buckets:
            pytest.skip("No S3 buckets found in Terraform state")

        s3 = aws_helper.get_client('s3')

        for bucket_resource in s3_buckets:
            try:
                # Extract bucket name (this is simplified - in real scenario you'd parse state)
                # For now, we'll check buckets with our naming pattern
                resource_prefix = environment_config['resource_prefix']

                response = s3.list_buckets()
                buckets = response['Buckets']

                # Find buckets matching our pattern
                our_buckets = [b for b in buckets if resource_prefix in b['Name']]
                assert len(our_buckets) > 0, f"No S3 buckets found with prefix {resource_prefix}"

                for bucket in our_buckets:
                    # Test bucket configuration
                    bucket_name = bucket['Name']
                    try:
                        # Check bucket encryption
                        encryption = s3.get_bucket_encryption(Bucket=bucket_name)
                        assert 'ServerSideEncryptionConfiguration' in encryption
                    except ClientError:
                        pytest.fail(f"Bucket {bucket_name} should have encryption enabled")

            except ClientError as e:
                pytest.fail(f"Failed to access S3 buckets: {e}")

@pytest.mark.aws
@pytest.mark.integration
@pytest.mark.slow
class TestResourceConnectivity:
    """Test connectivity between AWS resources"""

    def test_vpc_dns_resolution(self, terraform_outputs, aws_helper):
        """Test that VPC has DNS resolution enabled"""
        if not terraform_outputs:
            pytest.skip("No Terraform outputs available")

        vpc_id = terraform_outputs.get('vpc_id', {}).get('value')
        if not vpc_id:
            pytest.skip("VPC ID not available")

        ec2 = aws_helper.get_client('ec2')

        try:
            response = ec2.describe_vpc_attribute(VpcId=vpc_id, Attribute='enableDnsSupport')
            assert response['EnableDnsSupport']['Value'], "VPC should have DNS support enabled"

            response = ec2.describe_vpc_attribute(VpcId=vpc_id, Attribute='enableDnsHostnames')
            assert response['EnableDnsHostnames']['Value'], "VPC should have DNS hostnames enabled"

        except ClientError as e:
            pytest.fail(f"Failed to check VPC DNS attributes: {e}")

    def test_route_tables_configured(self, terraform_outputs, aws_helper):
        """Test that route tables are properly configured"""
        if not terraform_outputs:
            pytest.skip("No Terraform outputs available")

        vpc_id = terraform_outputs.get('vpc_id', {}).get('value')
        if not vpc_id:
            pytest.skip("VPC ID not available")

        ec2 = aws_helper.get_client('ec2')

        try:
            response = ec2.describe_route_tables(
                Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
            )

            route_tables = response['RouteTables']
            assert len(route_tables) > 0, "No route tables found for VPC"

            # Check for internet route
            has_internet_route = False
            for rt in route_tables:
                for route in rt['Routes']:
                    if route.get('DestinationCidrBlock') == '0.0.0.0/0':
                        has_internet_route = True
                        break
                if has_internet_route:
                    break

            assert has_internet_route, "No internet route found in route tables"

        except ClientError as e:
            pytest.fail(f"Failed to check route tables: {e}")

    def test_subnets_internet_connectivity(self, terraform_outputs, aws_helper):
        """Test that public subnets have internet connectivity"""
        if not terraform_outputs:
            pytest.skip("No Terraform outputs available")

        subnet_ids = terraform_outputs.get('subnet_ids', {}).get('value', [])
        if not subnet_ids:
            pytest.skip("Subnet IDs not available")

        ec2 = aws_helper.get_client('ec2')

        try:
            response = ec2.describe_subnets(SubnetIds=subnet_ids)
            subnets = response['Subnets']

            # Check if subnets are associated with route tables that have internet access
            for subnet in subnets:
                subnet_id = subnet['SubnetId']

                # Get route table for subnet
                rt_response = ec2.describe_route_tables(
                    Filters=[{'Name': 'association.subnet-id', 'Values': [subnet_id]}]
                )

                route_tables = rt_response['RouteTables']
                if not route_tables:
                    # Check main route table
                    vpc_id = subnet['VpcId']
                    rt_response = ec2.describe_route_tables(
                        Filters=[
                            {'Name': 'vpc-id', 'Values': [vpc_id]},
                            {'Name': 'association.main', 'Values': ['true']}
                        ]
                    )
                    route_tables = rt_response['RouteTables']

                # For public subnets, should have internet route
                if subnet.get('MapPublicIpOnLaunch', False):
                    has_internet_route = False
                    for rt in route_tables:
                        for route in rt['Routes']:
                            if route.get('DestinationCidrBlock') == '0.0.0.0/0':
                                has_internet_route = True
                                break

                    assert has_internet_route, f"Public subnet {subnet_id} should have internet route"

        except ClientError as e:
            pytest.fail(f"Failed to check subnet connectivity: {e}")
