# terraform/eks.tf
# Simple EKS cluster for prod environment

# EKS Cluster
resource "aws_eks_cluster" "main" {
  count = local.enable_prod ? 1 : 0

  name     = "${local.resource_prefix}-cluster"
  role_arn = aws_iam_role.eks_cluster[0].arn
  version  = "1.29"

  vpc_config {
    subnet_ids = concat(aws_subnet.private[*].id, aws_subnet.public[*].id)
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy
  ]

  tags = local.common_tags
}

# EKS Node Group
resource "aws_eks_node_group" "main" {
  count = local.enable_prod ? 1 : 0

  cluster_name    = aws_eks_cluster.main[0].name
  node_group_name = "${local.resource_prefix}-node-group"
  node_role_arn   = aws_iam_role.eks_node_group[0].arn
  subnet_ids      = aws_subnet.private[*].id

  scaling_config {
    desired_size = 2
    max_size     = 3
    min_size     = 1
  }

  instance_types = ["t3.small"]

  depends_on = [
    aws_iam_role_policy_attachment.eks_worker_node_policy,
    aws_iam_role_policy_attachment.eks_cni_policy,
    aws_iam_role_policy_attachment.eks_container_registry_policy,
  ]

  tags = local.common_tags
}

# LoadBalancer for API Gateway Service
resource "aws_lb" "api_gateway" {
  count = local.enable_prod ? 1 : 0

  name               = "op-prod-api-lb"
  internal           = false
  load_balancer_type = "network"
  subnets            = aws_subnet.public[*].id

  enable_deletion_protection = false

  tags = merge(local.common_tags, {
    Name = "${local.resource_prefix}-api-gateway-lb"
    Service = "api-gateway"
  })

  # Handle deletion dependencies
  lifecycle {
    create_before_destroy = true
  }
}

# LoadBalancer Target Group
resource "aws_lb_target_group" "api_gateway" {
  count = local.enable_prod ? 1 : 0

  name     = "op-prod-api-tg"
  port     = 8080
  protocol = "TCP"
  vpc_id   = aws_vpc.main[0].id

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }

  tags = local.common_tags
}

# LoadBalancer Listener
resource "aws_lb_listener" "api_gateway" {
  count = local.enable_prod ? 1 : 0

  load_balancer_arn = aws_lb.api_gateway[0].arn
  port              = "8080"
  protocol          = "TCP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api_gateway[0].arn
  }
}