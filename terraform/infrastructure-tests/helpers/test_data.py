#!/usr/bin/env python3
# File: terraform/infrastructure-tests/helpers/test_data.py
# Test fixtures and sample data
# Environment-specific test data (dev, staging, ci)
# Resource naming patterns and validation
# Security test scenarios and compliance checks
# Mock data for offline testing


import os
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import ipaddress

# Test configuration constants
TEST_ENVIRONMENTS = {
    "dev": {
        "aws_region": "us-west-2",
        "resource_prefix": "order-processor-dev",
        "vpc_cidr": "10.0.0.0/16",
        "availability_zones": ["us-west-2a", "us-west-2b"],
        "expected_subnets": 4,  # 2 public, 2 private
        "expected_security_groups": 3,  # ALB, ECS, RDS
        "enable_nat_gateway": True,
        "enable_vpn_gateway": False,
        "multi_az_deployment": True,
        "backup_retention_days": 7,
        "monitoring_enabled": True,
        "cost_optimization": "basic"
    },
    "staging": {
        "aws_region": "us-west-2",
        "resource_prefix": "order-processor-staging",
        "vpc_cidr": "10.1.0.0/16",
        "availability_zones": ["us-west-2a", "us-west-2b", "us-west-2c"],
        "expected_subnets": 6,  # 3 public, 3 private
        "expected_security_groups": 4,  # ALB, ECS, RDS, Redis
        "enable_nat_gateway": True,
        "enable_vpn_gateway": False,
        "multi_az_deployment": True,
        "backup_retention_days": 14,
        "monitoring_enabled": True,
        "cost_optimization": "standard"
    },
    "prod": {
        "aws_region": "us-west-2",
        "resource_prefix": "order-processor-prod",
        "vpc_cidr": "10.2.0.0/16",
        "availability_zones": ["us-west-2a", "us-west-2b", "us-west-2c"],
        "expected_subnets": 6,
        "expected_security_groups": 5,  # ALB, ECS, RDS, Redis, Bastion
        "enable_nat_gateway": True,
        "enable_vpn_gateway": True,
        "multi_az_deployment": True,
        "backup_retention_days": 30,
        "monitoring_enabled": True,
        "cost_optimization": "performance"
    },
    "ci": {
        "aws_region": "us-west-2",
        "resource_prefix": "order-processor-ci",
        "vpc_cidr": "10.3.0.0/16",
        "availability_zones": ["us-west-2a", "us-west-2b"],
        "expected_subnets": 4,
        "expected_security_groups": 3,
        "enable_nat_gateway": False,  # Cost optimization for CI
        "enable_vpn_gateway": False,
        "multi_az_deployment": False,
        "backup_retention_days": 1,
        "monitoring_enabled": False,
        "cost_optimization": "minimal"
    }
}

# Expected AWS resource naming patterns
RESOURCE_NAME_PATTERNS = {
    "vpc": "{prefix}-vpc",
    "public_subnet": "{prefix}-public-subnet-{az}",
    "private_subnet": "{prefix}-private-subnet-{az}",
    "database_subnet": "{prefix}-db-subnet-{az}",
    "internet_gateway": "{prefix}-igw",
    "nat_gateway": "{prefix}-nat-{az}",
    "elastic_ip": "{prefix}-eip-nat-{az}",
    "route_table_public": "{prefix}-public-rt",
    "route_table_private": "{prefix}-private-rt-{az}",
    "route_table_database": "{prefix}-db-rt",
    "security_group_alb": "{prefix}-alb-sg",
    "security_group_ecs": "{prefix}-ecs-sg",
    "security_group_rds": "{prefix}-rds-sg",
    "security_group_redis": "{prefix}-redis-sg",
    "security_group_bastion": "{prefix}-bastion-sg",
    "ecs_cluster": "{prefix}-cluster",
    "ecs_service": "{prefix}-{service_name}-service",
    "ecs_task_definition": "{prefix}-{service_name}-task",
    "alb": "{prefix}-alb",
    "alb_target_group": "{prefix}-{service_name}-tg",
    "s3_bucket_artifacts": "{prefix}-artifacts-{account_id}",
    "s3_bucket_logs": "{prefix}-logs-{account_id}",
    "s3_bucket_backups": "{prefix}-backups-{account_id}",
    "dynamodb_orders": "{prefix}-orders",
    "dynamodb_inventory": "{prefix}-inventory",
    "dynamodb_users": "{prefix}-users",
    "rds_cluster": "{prefix}-cluster",
    "rds_instance": "{prefix}-instance-{az}",
    "elasticache_subnet_group": "{prefix}-redis-subnet-group",
    "elasticache_cluster": "{prefix}-redis-cluster",
    "cloudwatch_log_group": "/aws/ecs/{prefix}-{service_name}",
    "iam_role_ecs_task": "{prefix}-ecs-task-role",
    "iam_role_ecs_execution": "{prefix}-ecs-execution-role"
}

# Security configuration test data
SECURITY_TEST_DATA = {
    "allowed_cidr_blocks": [
        "10.0.0.0/8",    # Private networks
        "172.16.0.0/12", # Private networks
        "192.168.0.0/16" # Private networks
    ],
    "forbidden_cidr_blocks": [
        "0.0.0.0/0"  # Should only be allowed for specific ports (80, 443)
    ],
    "allowed_public_ports": [80, 443, 8080, 8443],  # Common web ports
    "forbidden_public_ports": [22, 3389, 1433, 3306, 5432, 6379, 27017],  # SSH, RDP, DB ports
    "required_tags": ["Environment", "Project", "Owner", "CostCenter"],
    "optional_tags": ["Team", "Application", "Version"],
    "encryption_algorithms": ["AES256", "aws:kms"],
    "s3_security_requirements": {
        "block_public_acls": True,
        "block_public_policy": True,
        "ignore_public_acls": True,
        "restrict_public_buckets": True,
        "versioning_enabled": True,
        "encryption_enabled": True
    },
    "rds_security_requirements": {
        "encryption_at_rest": True,
        "encryption_in_transit": True,
        "backup_encryption": True,
        "multi_az": True,
        "deletion_protection": True
    },
    "ecs_security_requirements": {
        "task_role_required": True,
        "execution_role_required": True,
        "secrets_from_parameter_store": True,
        "container_insights": True
    }
}

# Sample configuration files for testing
SAMPLE_CONFIGS = {
    "dev_vars": {
        "environment": "dev",
        "aws_region": "us-west-2",
        "resource_prefix": "order-processor-dev",
        "vpc_cidr": "10.0.0.0/16",
        "availability_zones": ["us-west-2a", "us-west-2b"],
        "enable_nat_gateway": True,
        "enable_dns_hostnames": True,
        "enable_dns_support": True,
        "ecs_cluster_name": "order-processor-dev-cluster",
        "container_insights": True,
        "rds_instance_class": "db.t3.micro",
        "rds_allocated_storage": 20,
        "rds_max_allocated_storage": 100,
        "elasticache_node_type": "cache.t3.micro",
        "elasticache_num_cache_nodes": 1
    },
    "staging_vars": {
        "environment": "staging",
        "aws_region": "us-west-2",
        "resource_prefix": "order-processor-staging",
        "vpc_cidr": "10.1.0.0/16",
        "availability_zones": ["us-west-2a", "us-west-2b", "us-west-2c"],
        "enable_nat_gateway": True,
        "enable_dns_hostnames": True,
        "enable_dns_support": True,
        "ecs_cluster_name": "order-processor-staging-cluster",
        "container_insights": True,
        "rds_instance_class": "db.t3.small",
        "rds_allocated_storage": 100,
        "rds_max_allocated_storage": 500,
        "elasticache_node_type": "cache.t3.small",
        "elasticache_num_cache_nodes": 2
    },
    "minimal_vars": {
        "environment": "ci",
        "aws_region": "us-west-2",
        "resource_prefix": "test-minimal",
        "vpc_cidr": "10.3.0.0/16",
        "availability_zones": ["us-west-2a"],
        "enable_nat_gateway": False,
        "enable_dns_hostnames": True,
        "enable_dns_support": True
    }
}

# Test scenario data
TEST_SCENARIOS = {
    "basic_infrastructure": {
        "description": "Test basic VPC, subnets, and ECS cluster",
        "required_resources": [
            "aws_vpc.main",
            "aws_subnet.public",
            "aws_subnet.private",
            "aws_internet_gateway.main",
            "aws_route_table.public",
            "aws_route_table.private",
            "aws_ecs_cluster.main"
        ],
        "required_outputs": [
            "vpc_id",
            "public_subnet_ids",
            "private_subnet_ids",
            "ecs_cluster_name",
            "ecs_cluster_arn"
        ],
        "security_groups": ["alb", "ecs"],
        "estimated_cost_monthly": 50  # USD
    },
    "web_application": {
        "description": "Test web application infrastructure with ALB",
        "required_resources": [
            "aws_lb.main",
            "aws_lb_target_group.app",
            "aws_lb_listener.web",
            "aws_ecs_service.web",
            "aws_ecs_task_definition.web"
        ],
        "required_outputs": [
            "alb_dns_name",
            "alb_zone_id",
            "alb_arn",
            "target_group_arn"
        ],
        "security_groups": ["alb", "ecs"],
        "estimated_cost_monthly": 100
    },
    "database": {
        "description": "Test database infrastructure",
        "required_resources": [
            "aws_db_subnet_group.main",
            "aws_db_instance.main",
            "aws_db_parameter_group.main"
        ],
        "required_outputs": [
            "rds_endpoint",
            "rds_port",
            "rds_instance_id"
        ],
        "security_groups": ["rds"],
        "estimated_cost_monthly": 75
    },
    "cache_layer": {
        "description": "Test Redis cache infrastructure",
        "required_resources": [
            "aws_elasticache_subnet_group.main",
            "aws_elasticache_cluster.main",
            "aws_elasticache_parameter_group.main"
        ],
        "required_outputs": [
            "redis_endpoint",
            "redis_port",
            "redis_cluster_id"
        ],
        "security_groups": ["redis"],
        "estimated_cost_monthly": 30
    },
    "complete_stack": {
        "description": "Test complete application stack",
        "required_resources": [
            # Network
            "aws_vpc.main",
            "aws_subnet.public",
            "aws_subnet.private",
            "aws_subnet.database",
            "aws_internet_gateway.main",
            "aws_nat_gateway.main",
            # Security
            "aws_security_group.alb",
            "aws_security_group.ecs",
            "aws_security_group.rds",
            # Compute
            "aws_ecs_cluster.main",
            "aws_ecs_service.web",
            "aws_ecs_service.api",
            # Load Balancing
            "aws_lb.main",
            "aws_lb_target_group.web",
            "aws_lb_target_group.api",
            # Database
            "aws_db_instance.main",
            # Storage
            "aws_s3_bucket.artifacts",
            "aws_s3_bucket.logs"
        ],
        "required_outputs": [
            "vpc_id",
            "alb_dns_name",
            "ecs_cluster_name",
            "rds_endpoint",
            "s3_bucket_artifacts",
            "s3_bucket_logs"
        ],
        "security_groups": ["alb", "ecs", "rds"],
        "estimated_cost_monthly": 300
    }
}

# Performance and load testing data
PERFORMANCE_TEST_DATA = {
    "load_test_scenarios": {
        "light_load": {
            "concurrent_users": 10,
            "requests_per_second": 5,
            "duration_minutes": 5
        },
        "medium_load": {
            "concurrent_users": 50,
            "requests_per_second": 25,
            "duration_minutes": 10
        },
        "heavy_load": {
            "concurrent_users": 200,
            "requests_per_second": 100,
            "duration_minutes": 15
        }
    },
    "expected_response_times": {
        "health_check": {"max_ms": 100, "avg_ms": 50},
        "api_endpoints": {"max_ms": 500, "avg_ms": 200},
        "database_queries": {"max_ms": 1000, "avg_ms": 300}
    },
    "resource_limits": {
        "cpu_utilization_max": 80,
        "memory_utilization_max": 85,
        "disk_utilization_max": 80,
        "network_utilization_max": 70
    }
}

# Disaster recovery test scenarios
DISASTER_RECOVERY_TEST_DATA = {
    "scenarios": {
        "single_az_failure": {
            "description": "Simulate single AZ failure",
            "impact": "partial_service_degradation",
            "recovery_time_objective": 300,  # seconds
            "recovery_point_objective": 60   # seconds
        },
        "database_failover": {
            "description": "Test RDS failover to standby",
            "impact": "temporary_unavailability",
            "recovery_time_objective": 180,
            "recovery_point_objective": 30
        },
        "complete_region_failure": {
            "description": "Test cross-region disaster recovery",
            "impact": "full_service_outage",
            "recovery_time_objective": 3600,
            "recovery_point_objective": 300
        }
    }
}

# Common test utilities
def get_expected_resource_name(resource_type: str, **kwargs) -> str:
    """Generate expected resource name based on naming convention"""
    pattern = RESOURCE_NAME_PATTERNS.get(resource_type)
    if not pattern:
        raise ValueError(f"No naming pattern defined for resource type: {resource_type}")

    return pattern.format(**kwargs)

def get_test_config_for_environment(env: str) -> Dict[str, Any]:
    """Get test configuration for specific environment"""
    if env not in TEST_ENVIRONMENTS:
        raise ValueError(f"No test configuration for environment: {env}")

    return TEST_ENVIRONMENTS[env].copy()

def validate_resource_tags(tags: Dict[str, str], environment: str) -> List[str]:
    """Validate that resource has required tags"""
    errors = []

    for required_tag in SECURITY_TEST_DATA["required_tags"]:
        if required_tag not in tags:
            errors.append(f"Missing required tag: {required_tag}")

    if "Environment" in tags and tags["Environment"] != environment:
        errors.append(f"Environment tag mismatch: expected {environment}, got {tags['Environment']}")

    return errors

def is_cidr_allowed_for_port(cidr: str, port: int) -> bool:
    """Check if CIDR block is allowed for specific port"""
    if cidr == "0.0.0.0/0":
        return port in SECURITY_TEST_DATA["allowed_public_ports"]

    return cidr in SECURITY_TEST_DATA["allowed_cidr_blocks"]

def validate_vpc_cidr(cidr: str) -> Tuple[bool, str]:
    """Validate VPC CIDR block"""
    try:
        network = ipaddress.IPv4Network(cidr, strict=False)

        # Check if it's a private network
        if not network.is_private:
            return False, f"CIDR {cidr} is not a private network"

        # Check CIDR size (should be between /16 and /28)
        if network.prefixlen < 16:
            return False, f"CIDR {cidr} is too large (prefix < /16)"
        if network.prefixlen > 28:
            return False, f"CIDR {cidr} is too small (prefix > /28)"

        return True, ""

    except ValueError as e:
        return False, f"Invalid CIDR format: {e}"

def generate_subnet_cidrs(vpc_cidr: str, num_subnets: int) -> List[str]:
    """Generate subnet CIDR blocks from VPC CIDR"""
    try:
        vpc_network = ipaddress.IPv4Network(vpc_cidr, strict=False)

        # Calculate subnet size based on number of subnets needed
        # Add some buffer for future expansion
        required_subnets = num_subnets * 2
        subnet_bits = (required_subnets - 1).bit_length()
        new_prefix = vpc_network.prefixlen + subnet_bits

        if new_prefix > 28:
            raise ValueError(f"Cannot create {num_subnets} subnets in {vpc_cidr}")

        subnets = list(vpc_network.subnets(new_prefix=new_prefix))
        return [str(subnet) for subnet in subnets[:num_subnets]]

    except ValueError as e:
        raise ValueError(f"Failed to generate subnets: {e}")

def get_availability_zones_for_region(region: str) -> List[str]:
    """Get expected availability zones for AWS region"""
    az_mapping = {
        "us-east-1": ["us-east-1a", "us-east-1b", "us-east-1c", "us-east-1d"],
        "us-west-2": ["us-west-2a", "us-west-2b", "us-west-2c", "us-west-2d"],
        "eu-west-1": ["eu-west-1a", "eu-west-1b", "eu-west-1c"],
        "ap-southeast-1": ["ap-southeast-1a", "ap-southeast-1b", "ap-southeast-1c"]
    }

    return az_mapping.get(region, [f"{region}a", f"{region}b"])

def calculate_estimated_monthly_cost(scenario: str, environment: str) -> float:
    """Calculate estimated monthly cost for test scenario"""
    if scenario not in TEST_SCENARIOS:
        return 0.0

    base_cost = TEST_SCENARIOS[scenario].get("estimated_cost_monthly", 0)

    # Apply environment multipliers
    env_multipliers = {
        "ci": 0.3,     # Minimal resources
        "dev": 0.5,    # Reduced resources
        "staging": 0.8, # Near-production
        "prod": 1.5    # Full production with redundancy
    }

    multiplier = env_multipliers.get(environment, 1.0)
    return base_cost * multiplier

def get_security_compliance_checklist(environment: str) -> Dict[str, List[str]]:
    """Get security compliance checklist for environment"""
    base_checklist = {
        "encryption": [
            "S3 buckets encrypted at rest",
            "RDS instances encrypted at rest",
            "EBS volumes encrypted",
            "ELB uses TLS 1.2 or higher"
        ],
        "access_control": [
            "No public S3 buckets",
            "Security groups follow least privilege",
            "IAM roles use minimal permissions",
            "No hardcoded credentials"
        ],
        "monitoring": [
            "CloudTrail enabled",
            "CloudWatch monitoring configured",
            "Access logging enabled",
            "Security alerts configured"
        ],
        "network": [
            "Private subnets for databases",
            "NAT gateways for outbound traffic",
            "Network ACLs configured",
            "VPC Flow Logs enabled"
        ]
    }

    # Add environment-specific requirements
    if environment == "prod":
        base_checklist["compliance"] = [
            "Data backup strategy implemented",
            "Disaster recovery plan tested",
            "Security audit completed",
            "Compliance documentation updated"
        ]

    return base_checklist

# Mock data for testing (when AWS resources aren't available)
MOCK_TERRAFORM_OUTPUTS = {
    "vpc_id": {"value": "vpc-12345678"},
    "public_subnet_ids": {"value": ["subnet-12345678", "subnet-87654321"]},
    "private_subnet_ids": {"value": ["subnet-abcdef12", "subnet-fedcba21"]},
    "ecs_cluster_name": {"value": "order-processor-dev-cluster"},
    "ecs_cluster_arn": {"value": "arn:aws:ecs:us-west-2:123456789012:cluster/order-processor-dev-cluster"},
    "security_group_ids": {"value": ["sg-12345678", "sg-87654321"]},
    "alb_dns_name": {"value": "order-processor-dev-alb-123456789.us-west-2.elb.amazonaws.com"},
    "alb_arn": {"value": "arn:aws:elasticloadbalancing:us-west-2:123456789012:loadbalancer/app/order-processor-dev-alb/1234567890123456"},
    "rds_endpoint": {"value": "order-processor-dev-cluster.cluster-xyz.us-west-2.rds.amazonaws.com"},
    "rds_port": {"value": "5432"},
    "redis_endpoint": {"value": "order-processor-dev-redis.abc123.cache.amazonaws.com"},
    "redis_port": {"value": "6379"},
    "s3_bucket_artifacts": {"value": "order-processor-dev-artifacts-123456789012"},
    "s3_bucket_logs": {"value": "order-processor-dev-logs-123456789012"}
}

MOCK_TERRAFORM_STATE = [
    "aws_vpc.main",
    "aws_subnet.public[0]",
    "aws_subnet.public[1]",
    "aws_subnet.private[0]",
    "aws_subnet.private[1]",
    "aws_subnet.database[0]",
    "aws_subnet.database[1]",
    "aws_internet_gateway.main",
    "aws_nat_gateway.main[0]",
    "aws_nat_gateway.main[1]",
    "aws_route_table.public",
    "aws_route_table.private[0]",
    "aws_route_table.private[1]",
    "aws_route_table.database",
    "aws_security_group.alb",
    "aws_security_group.ecs",
    "aws_security_group.rds",
    "aws_ecs_cluster.main",
    "aws_ecs_service.web",
    "aws_ecs_service.api",
    "aws_ecs_task_definition.web",
    "aws_ecs_task_definition.api",
    "aws_lb.main",
    "aws_lb_target_group.web",
    "aws_lb_target_group.api",
    "aws_lb_listener.web",
    "aws_lb_listener.api",
    "aws_s3_bucket.artifacts",
    "aws_s3_bucket.logs",
    "aws_db_instance.main",
    "aws_db_subnet_group.main",
    "aws_elasticache_cluster.main",
    "aws_elasticache_subnet_group.main",
    "aws_dynamodb_table.orders",
    "aws_dynamodb_table.inventory"
]

# Test data validation functions
def validate_test_environment_config(env_config: Dict[str, Any]) -> List[str]:
    """Validate test environment configuration"""
    errors = []

    required_keys = [
        "aws_region", "resource_prefix", "vpc_cidr",
        "availability_zones", "expected_subnets"
    ]

    for key in required_keys:
        if key not in env_config:
            errors.append(f"Missing required configuration key: {key}")

    if "vpc_cidr" in env_config:
        is_valid, error_msg = validate_vpc_cidr(env_config["vpc_cidr"])
        if not is_valid:
            errors.append(f"Invalid VPC CIDR: {error_msg}")

    return errors

def get_test_data_summary() -> Dict[str, Any]:
    """Get summary of available test data"""
    return {
        "environments": list(TEST_ENVIRONMENTS.keys()),
        "resource_patterns": len(RESOURCE_NAME_PATTERNS),
        "test_scenarios": list(TEST_SCENARIOS.keys()),
        "security_checks": len(SECURITY_TEST_DATA["required_tags"]),
        "mock_outputs": len(MOCK_TERRAFORM_OUTPUTS),
        "mock_state_resources": len(MOCK_TERRAFORM_STATE)
    }