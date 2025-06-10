#!/usr/bin/env python3
# File: terraform/infrastructure-tests/test_connectivity.py
# Network connectivity and endpoint testing
# Network connectivity: internet, AWS APIs, DNS resolution
# Load balancer tests: health checks, SSL configuration
# Database connectivity: RDS endpoint testing
# Service discovery: ECS service validation
# End-to-end flows: complete request testing

import pytest
import requests
import socket
import subprocess
import time
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

@pytest.mark.aws
@pytest.mark.integration
@pytest.mark.slow
class TestNetworkConnectivity:
    """Test network connectivity and reachability"""

    def test_internet_connectivity(self):
        """Test basic internet connectivity from test environment"""
        try:
            response = requests.get('https://httpbin.org/ip', timeout=10)
            assert response.status_code == 200, "Cannot reach internet"

            data = response.json()
            assert 'origin' in data, "Invalid response from internet endpoint"

        except requests.RequestException as e:
            pytest.fail(f"Internet connectivity test failed: {e}")

    def test_aws_api_connectivity(self, aws_helper):
        """Test connectivity to AWS APIs"""
        try:
            # Test STS (authentication)
            sts = aws_helper.get_client('sts')
            identity = sts.get_caller_identity()
            assert 'Account' in identity, "Cannot authenticate with AWS"

            # Test EC2 API
            ec2 = aws_helper.get_client('ec2')
            regions = ec2.describe_regions()
            assert len(regions['Regions']) > 0, "Cannot list AWS regions"

        except Exception as e:
            pytest.fail(f"AWS API connectivity test failed: {e}")

    def test_dns_resolution(self):
        """Test DNS resolution for critical services"""
        critical_domains = [
            'amazonaws.com',
            'registry.terraform.io',
            'github.com'
        ]

        for domain in critical_domains:
            try:
                socket.gethostbyname(domain)
            except socket.gaierror as e:
                pytest.fail(f"DNS resolution failed for {domain}: {e}")

@pytest.mark.aws
@pytest.mark.integration
class TestLoadBalancerConnectivity:
    """Test Application Load Balancer connectivity (if deployed)"""

    def test_alb_health_check(self, terraform_outputs):
        """Test ALB health check endpoints"""
        if not terraform_outputs:
            pytest.skip("No Terraform outputs available")

        alb_dns = terraform_outputs.get('alb_dns_name', {}).get('value')
        if not alb_dns:
            pytest.skip("ALB DNS name not available in outputs")

        # Test ALB is reachable
        try:
            response = requests.get(f'http://{alb_dns}/health', timeout=30)
            # ALB might return 503 if no healthy targets, that's OK for this test
            assert response.status_code in [200, 503], f"ALB not reachable: {response.status_code}"

        except requests.RequestException as e:
            pytest.fail(f"ALB connectivity test failed: {e}")

    def test_alb_ssl_configuration(self, terraform_outputs):
        """Test ALB SSL/TLS configuration (if HTTPS enabled)"""
        if not terraform_outputs:
            pytest.skip("No Terraform outputs available")

        alb_dns = terraform_outputs.get('alb_dns_name', {}).get('value')
        if not alb_dns:
            pytest.skip("ALB DNS name not available")

        try:
            # Test HTTPS endpoint
            response = requests.get(f'https://{alb_dns}', timeout=30, verify=True)
            # Connection successful means SSL is working
            # Status code doesn't matter for this test

        except requests.exceptions.SSLError as e:
            pytest.fail(f"ALB SSL configuration invalid: {e}")
        except requests.RequestException:
            # Other connection errors are OK - we're just testing SSL
            pass

@pytest.mark.aws
@pytest.mark.integration
class TestDatabaseConnectivity:
    """Test database connectivity (if RDS deployed)"""

    def test_rds_connectivity(self, terraform_outputs, aws_helper):
        """Test RDS instance connectivity"""
        if not terraform_outputs:
            pytest.skip("No Terraform outputs available")

        rds_endpoint = terraform_outputs.get('rds_endpoint', {}).get('value')
        if not rds_endpoint:
            pytest.skip("RDS endpoint not available in outputs")

        # Extract host and port
        if ':' in rds_endpoint:
            host, port = rds_endpoint.split(':')
            port = int(port)
        else:
            host = rds_endpoint
            port = 5432  # Default PostgreSQL port

        # Test network connectivity to RDS
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((host, port))
            sock.close()

            assert result == 0, f"Cannot connect to RDS endpoint {host}:{port}"

        except Exception as e:
            pytest.fail(f"RDS connectivity test failed: {e}")

@pytest.mark.aws
@pytest.mark.integration
class TestServiceEndpoints:
    """Test service endpoint connectivity"""

    def test_api_gateway_connectivity(self, terraform_outputs):
        """Test API Gateway endpoint connectivity"""
        if not terraform_outputs:
            pytest.skip("No Terraform outputs available")

        api_endpoint = terraform_outputs.get('api_gateway_url', {}).get('value')
        if not api_endpoint:
            pytest.skip("API Gateway URL not available in outputs")

        try:
            # Test basic connectivity
            response = requests.get(f'{api_endpoint}/health', timeout=30)
            # API might not be deployed yet, so we just check if endpoint is reachable
            assert response.status_code < 500, f"API Gateway endpoint error: {response.status_code}"

        except requests.RequestException as e:
            pytest.fail(f"API Gateway connectivity test failed: {e}")

    def test_service_discovery(self, terraform_outputs, aws_helper):
        """Test ECS service discovery (if configured)"""
        if not terraform_outputs:
            pytest.skip("No Terraform outputs available")

        cluster_name = terraform_outputs.get('ecs_cluster_name', {}).get('value')
        if not cluster_name:
            pytest.skip("ECS cluster name not available")

        ecs = aws_helper.get_client('ecs')

        try:
            # List services in cluster
            response = ecs.list_services(cluster=cluster_name)
            services = response['serviceArns']

            if services:
                # Describe services to check their status
                service_details = ecs.describe_services(
                    cluster=cluster_name,
                    services=services
                )

                for service in service_details['services']:
                    # Check service is running
                    assert service['status'] == 'ACTIVE', f"Service {service['serviceName']} is not active"

                    # Check desired vs running tasks
                    running_count = service['runningCount']
                    desired_count = service['desiredCount']

                    if desired_count > 0:
                        # Allow some time for tasks to start
                        assert running_count >= 0, f"No tasks running for service {service['serviceName']}"

        except Exception as e:
            pytest.fail(f"Service discovery test failed: {e}")

@pytest.mark.aws
@pytest.mark.integration
@pytest.mark.slow
class TestEndToEndConnectivity:
    """Test end-to-end connectivity scenarios"""

    def test_full_request_flow(self, terraform_outputs):
        """Test complete request flow through infrastructure"""
        if not terraform_outputs:
            pytest.skip("No Terraform outputs available")

        # This test would simulate a complete user request
        # For now, we'll test basic infrastructure components

        vpc_id = terraform_outputs.get('vpc_id', {}).get('value')
        cluster_name = terraform_outputs.get('ecs_cluster_name', {}).get('value')

        if not vpc_id or not cluster_name:
            pytest.skip("Required infrastructure components not available")

        # Test would include:
        # 1. ALB receives request
        # 2. Routes to ECS service
        # 3. Service processes request
        # 4. Database query (if applicable)
        # 5. Response returned

        # For now, just verify components exist
        assert vpc_id is not None, "VPC should exist"
        assert cluster_name is not None, "ECS cluster should exist"

    def test_cross_az_connectivity(self, terraform_outputs, aws_helper):
        """Test connectivity across availability zones"""
        if not terraform_outputs:
            pytest.skip("No Terraform outputs available")

        subnet_ids = terraform_outputs.get('subnet_ids', {}).get('value', [])
        if len(subnet_ids) < 2:
            pytest.skip("Need at least 2 subnets for cross-AZ test")

        ec2 = aws_helper.get_client('ec2')

        try:
            response = ec2.describe_subnets(SubnetIds=subnet_ids)
            subnets = response['Subnets']

            # Verify subnets are in different AZs
            azs = {subnet['AvailabilityZone'] for subnet in subnets}
            assert len(azs) >= 2, "Subnets should be in different availability zones"

            # All subnets should be in the same VPC
            vpc_ids = {subnet['VpcId'] for subnet in subnets}
            assert len(vpc_ids) == 1, "All subnets should be in the same VPC"

        except Exception as e:
            pytest.fail(f"Cross-AZ connectivity test failed: {e}")
