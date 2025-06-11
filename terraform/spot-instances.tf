# ===== SPOT INSTANCES CONFIGURATION =====
# spot-instances.tf

# Local values for spot instance configuration
locals {
  # Spot instance configuration by cost profile
  spot_config = {
    minimal = {
      instance_types = ["t3.micro", "t4g.micro"]
      desired_size   = 1
      max_size       = 2
      min_size       = 1
    }
    learning = {
      instance_types = ["t3.small", "t4g.small", "t3.medium"]
      desired_size   = 2
      max_size       = 4
      min_size       = 1
    }
    production = {
      instance_types = ["t3.medium", "t3.large", "m5.large"]
      desired_size   = 3
      max_size       = 10
      min_size       = 2
    }
  }

  # Current configuration
  current_spot_config = local.spot_config[var.cost_profile]

  # Spot instance tags
  spot_tags = {
    NodeType = "spot"
    CostOptimization = "spot-instances"
    InterruptionTolerant = "true"
    Purpose = "cost-efficient-compute"
  }
}

# SPOT INSTANCES: EKS Node Group with Spot Instances (alternative to Fargate)
resource "aws_eks_node_group" "spot_nodes" {
  count = var.use_spot_instances ? 1 : 0

  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "${var.project_name}-${var.environment}-spot-nodes"
  node_role_arn   = aws_iam_role.eks_spot_node_group[0].arn
  subnet_ids      = aws_subnet.private[*].id

  # COST OPTIMIZATION: Use SPOT capacity type for 60-90% savings
  capacity_type  = "SPOT"
  instance_types = local.current_spot_config.instance_types

  scaling_config {
    desired_size = local.current_spot_config.desired_size
    max_size     = local.current_spot_config.max_size
    min_size     = local.current_spot_config.min_size
  }

  update_config {
    max_unavailable_percentage = 50  # Allow 50% unavailable during updates
  }

  # COST OPTIMIZATION: Use latest Amazon Linux 2 AMI to avoid AMI costs
  ami_type       = "AL2_x86_64"
  disk_size      = 20  # Minimum disk size

  # COST OPTIMIZATION: Instance refresh settings for spot interruptions
  instance_types = local.current_spot_config.instance_types

  # Launch template for advanced spot configuration
  launch_template {
    id      = aws_launch_template.spot_nodes[0].id
    version = aws_launch_template.spot_nodes[0].latest_version
  }

  tags = merge(local.spot_tags, {
    Name = "${var.project_name}-${var.environment}-spot-nodes"
  })

  # Ensure proper dependencies
  depends_on = [
    aws_iam_role_policy_attachment.eks_spot_worker_node_policy,
    aws_iam_role_policy_attachment.eks_spot_cni_policy,
    aws_iam_role_policy_attachment.eks_spot_container_registry_policy,
  ]

  # Allow external changes to scaling
  lifecycle {
    ignore_changes = [scaling_config[0].desired_size]
  }
}

# SPOT INSTANCES: Launch template for spot node configuration
resource "aws_launch_template" "spot_nodes" {
  count = var.use_spot_instances ? 1 : 0

  name_prefix = "${var.project_name}-${var.environment}-spot-"
  description = "Launch template for spot instances"

  # COST OPTIMIZATION: Spot market configuration
  instance_market_options {
    market_type = "spot"
    spot_options {
      spot_instance_type = "one-time"
      # Don't set max_price to use current spot price
    }
  }

  # COST OPTIMIZATION: Optimized instance configuration
  instance_type = local.current_spot_config.instance_types[0]  # Primary instance type

  block_device_mappings {
    device_name = "/dev/xvda"
    ebs {
      volume_size = 20
      volume_type = "gp3"  # gp3 is 20% cheaper than gp2
      encrypted   = true
      delete_on_termination = true
    }
  }

  vpc_security_group_ids = [aws_security_group.spot_nodes[0].id]

  # User data for EKS node registration
  user_data = base64encode(templatefile("${path.module}/scripts/spot-node-userdata.sh", {
    cluster_name = aws_eks_cluster.main.name
    endpoint     = aws_eks_cluster.main.endpoint
    ca_data      = aws_eks_cluster.main.certificate_authority[0].data
  }))

  tag_specifications {
    resource_type = "instance"
    tags = merge(local.spot_tags, {
      Name = "${var.project_name}-${var.environment}-spot-node"
    })
  }

  tag_specifications {
    resource_type = "volume"
    tags = merge(local.spot_tags, {
      Name = "${var.project_name}-${var.environment}-spot-volume"
    })
  }

  tags = local.spot_tags
}

# SPOT INSTANCES: Security group for spot nodes
resource "aws_security_group" "spot_nodes" {
  count = var.use_spot_instances ? 1 : 0

  name_prefix = "${var.project_name}-${var.environment}-spot-nodes-"
  vpc_id      = aws_vpc.main.id
  description = "Security group for EKS spot instances"

  # Allow communication with EKS cluster
  ingress {
    description = "HTTPS from EKS cluster"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    security_groups = [aws_security_group.eks_cluster[0].id]
  }

  # Allow communication between nodes
  ingress {
    description = "All traffic from other nodes"
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    self        = true
  }

  # Allow kubelet communication
  ingress {
    description = "Kubelet"
    from_port   = 10250
    to_port     = 10250
    protocol    = "tcp"
    security_groups = [aws_security_group.eks_cluster[0].id]
  }

  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.spot_tags, {
    Name = "${var.project_name}-${var.environment}-spot-nodes-sg"
  })
}

# SPOT INSTANCES: Security group for EKS cluster to communicate with spot nodes
resource "aws_security_group" "eks_cluster" {
  count = var.use_spot_instances ? 1 : 0

  name_prefix = "${var.project_name}-${var.environment}-eks-cluster-"
  vpc_id      = aws_vpc.main.id
  description = "Security group for EKS cluster"

  egress {
    description = "HTTPS to worker nodes"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    security_groups = [aws_security_group.spot_nodes[0].id]
  }

  egress {
    description = "Kubelet to worker nodes"
    from_port   = 10250
    to_port     = 10250
    protocol    = "tcp"
    security_groups = [aws_security_group.spot_nodes[0].id]
  }

  tags = merge(local.spot_tags, {
    Name = "${var.project_name}-${var.environment}-eks-cluster-sg"
  })
}

# SPOT INSTANCES: IAM role for spot node group
resource "aws_iam_role" "eks_spot_node_group" {
  count = var.use_spot_instances ? 1 : 0

  name = "${var.project_name}-${var.environment}-eks-spot-node-group-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = local.spot_tags
}

# Required IAM policies for spot node group
resource "aws_iam_role_policy_attachment" "eks_spot_worker_node_policy" {
  count = var.use_spot_instances ? 1 : 0

  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.eks_spot_node_group[0].name
}

resource "aws_iam_role_policy_attachment" "eks_spot_cni_policy" {
  count = var.use_spot_instances ? 1 : 0

  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.eks_spot_node_group[0].name
}

resource "aws_iam_role_policy_attachment" "eks_spot_container_registry_policy" {
  count = var.use_spot_instances ? 1 : 0

  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.eks_spot_node_group[0].name
}

# SPOT INSTANCES: Auto Scaling Group for additional cost optimization
resource "aws_autoscaling_group" "spot_asg" {
  count = var.cost_profile == "minimal" && var.use_spot_instances ? 1 : 0

  name                = "${var.project_name}-${var.environment}-spot-asg"
  vpc_zone_identifier = aws_subnet.private[*].id
  target_group_arns   = []
  health_check_type   = "EC2"
  health_check_grace_period = 300

  min_size         = 1
  max_size         = 3
  desired_capacity = 1

  # COST OPTIMIZATION: Mixed instances policy for maximum savings
  mixed_instances_policy {
    launch_template {
      launch_template_specification {
        launch_template_id = aws_launch_template.spot_nodes[0].id
        version            = "$Latest"
      }

      # Override instance types for diversification
      dynamic "override" {
        for_each = local.current_spot_config.instance_types
        content {
          instance_type = override.value
        }
      }
    }

    instances_distribution {
      on_demand_base_capacity                  = 0    # No on-demand instances
      on_demand_percentage_above_base_capacity = 0    # 100% spot
      spot_allocation_strategy                 = "price-capacity-optimized"
      spot_instance_pools                      = 3    # Diversify across pools
    }
  }

  # Scaling policies for cost optimization
  enabled_metrics = [
    "GroupMinSize",
    "GroupMaxSize",
    "GroupDesiredCapacity",
    "GroupInServiceInstances",
    "GroupTotalInstances"
  ]

  tag {
    key                 = "Name"
    value               = "${var.project_name}-${var.environment}-spot-asg"
    propagate_at_launch = true
  }

  tag {
    key                 = "kubernetes.io/cluster/${aws_eks_cluster.main.name}"
    value               = "owned"
    propagate_at_launch = true
  }

  dynamic "tag" {
    for_each = local.spot_tags
    content {
      key                 = tag.key
      value               = tag.value
      propagate_at_launch = true
    }
  }

  # Protect against accidental termination during learning
  protect_from_scale_in = false
}

# SPOT INSTANCES: CloudWatch alarms for spot interruption monitoring
resource "aws_cloudwatch_metric_alarm" "spot_interruption_alarm" {
  count = var.use_spot_instances ? 1 : 0

  alarm_name          = "${var.project_name}-${var.environment}-spot-interruptions"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "SpotInstanceTerminating"
  namespace           = "AWS/EC2"
  period              = "300"
  statistic           = "Sum"
  threshold           = "0"
  alarm_description   = "This metric monitors spot instance interruptions"
  alarm_actions       = [aws_sns_topic.cost_alerts.arn]

  dimensions = {
    AutoScalingGroupName = var.cost_profile == "minimal" ? aws_autoscaling_group.spot_asg[0].name : ""
  }

  tags = local.spot_tags
}

# Outputs for spot instance information
output "spot_instances_info" {
  description = "Spot instances configuration and cost savings"
  value = var.use_spot_instances ? {
    node_group_name = aws_eks_node_group.spot_nodes[0].node_group_name
    instance_types = local.current_spot_config.instance_types
    scaling_config = local.current_spot_config
    estimated_savings = "60-90% vs on-demand instances"
    cost_per_hour_estimate = var.cost_profile == "minimal" ? "$0.003-0.008/hour" : "$0.006-0.020/hour"
    interruption_handling = "Automatic instance replacement via Auto Scaling"
    monitoring_alarm = aws_cloudwatch_metric_alarm.spot_interruption_alarm[0].alarm_name
  } : {
    enabled = false
    reason = "Spot instances disabled - using Fargate instead"
  }
}

output "spot_cost_optimization_tips" {
  description = "Tips for optimizing spot instance costs"
  value = {
    diversification = "Multiple instance types reduce interruption risk"
    allocation_strategy = "price-capacity-optimized for best balance"
    scaling_tips = "Set appropriate min/max to handle interruptions"
    monitoring = "Watch CloudWatch alarms for interruption patterns"
    best_practices = [
      "Use multiple instance types and AZs",
      "Design applications to handle interruptions gracefully",
      "Monitor spot price history for optimal timing",
      "Use Auto Scaling Groups for automatic replacement"
    ]
  }
}