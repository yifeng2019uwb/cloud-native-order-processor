# terraform/locals.tf
# Centralized constants and naming for all Terraform resources

locals {
  # ====================
  # ENVIRONMENT FLAGS
  # ====================
  enable_prod = var.environment == "prod"
  enable_dev  = var.environment == "dev"

  # ====================
  # INFRASTRUCTURE FLAGS
  # ====================
  create_vpc = local.enable_prod
  create_eks = local.enable_prod
  create_rds = local.enable_prod
  create_redis = local.enable_prod

  # ====================
  # NAMING CONVENTIONS
  # ====================
  # Base naming
  project_name = var.project_name
  environment  = var.environment
  region       = var.region

  # Resource prefixes and suffixes
  resource_prefix = "${local.project_name}-${local.environment}"
  resource_suffix = "${local.environment}"

  # Service-specific naming
  service_names = {
    user_service     = "user-service"
    inventory_service = "inventory-service"
    frontend         = "frontend"
  }

  # Database naming
  db_names = {
    users_table     = "${local.resource_prefix}-users"
    orders_table    = "${local.resource_prefix}-orders"
    inventory_table = "${local.resource_prefix}-inventory"
    assets_table    = "${local.resource_prefix}-assets"
  }

  # Storage naming
  storage_names = {
    main_bucket     = "${local.resource_prefix}-main"
    logs_bucket     = "${local.resource_prefix}-logs"
    events_bucket   = "${local.resource_prefix}-events"
    backups_bucket  = "${local.resource_prefix}-backups"
  }

  # Queue naming
  queue_names = {
    order_processing = "${local.resource_prefix}-order-processing"
    order_dlq        = "${local.resource_prefix}-order-dlq"
  }

  # Topic naming
  topic_names = {
    order_events = "${local.resource_prefix}-order-events"
  }

  # ECR repository naming
  ecr_names = {
    user_service     = "${local.resource_prefix}-user-service"
    inventory_service = "${local.resource_prefix}-inventory-service"
    frontend         = "${local.resource_prefix}-frontend"
  }

  # Redis naming
  redis_names = {
    subnet_group = "${local.resource_prefix}-redis-subnet-group"
    security_group = "${local.resource_prefix}-redis-sg"
    cluster = "${local.resource_prefix}-redis"
  }

  # VPC naming
  vpc_names = {
    public_subnet = "${local.resource_prefix}-public-subnet"
    private_subnet = "${local.resource_prefix}-private-subnet"
    nat_eip = "${local.resource_prefix}-nat-eip"
    public_rt = "${local.resource_prefix}-public-rt"
    private_rt = "${local.resource_prefix}-private-rt"
    igw = "${local.resource_prefix}-igw"
    nat = "${local.resource_prefix}-nat"
  }

  # Security Group naming
  sg_names = {
    eks_cluster = "${local.resource_prefix}-eks-cluster-sg"
  }

  # IAM naming
  iam_names = {
    k8s_sa_role = "${local.resource_prefix}-k8s-sa-role"
    service_db_role = "${local.resource_prefix}-db-role"
    service_s3_role = "${local.resource_prefix}-s3-role"
    service_sqs_role = "${local.resource_prefix}-sqs-role"
    service_sns_role = "${local.resource_prefix}-sns-role"
    service_ecr_role = "${local.resource_prefix}-ecr-role"
    service_secrets_role = "${local.resource_prefix}-secrets-role"
    service_redis_role = "${local.resource_prefix}-redis-role"
    application_user = "${local.resource_prefix}-application-user"
    eks_cluster_role = "${local.resource_prefix}-eks-cluster-role"
  }

  # ====================
  # CONFIGURATION
  # ====================
  # Data lifecycle configuration (1 days = 1 years in personal project)
  data_lifecycle = {
    retention_days = 10    # Keep data for 10 days (equivalent to 10 years)
    archive_days   = 3     # Move to S3 after 3 day (equivalent to 3 year)
  }

  # Redis configuration
  redis_config = {
    node_type = "cache.t3.micro"  # Free tier eligible
    port      = 6379
    engine    = "redis"
    version   = "7"
  }

  # EKS configuration
  eks_config = {
    cluster_name = "${local.resource_prefix}-cluster"
    node_type    = "t3.medium"  # 2 vCPU, 4GB RAM
    min_size     = 1
    max_size     = 3
    desired_size = 1
  }

  # ====================
  # TAGS
  # ====================
  common_tags = {
    Environment = local.environment
    Project     = local.project_name
    ManagedBy   = "terraform"
    Owner       = "personal"
    CostCenter  = "learning"
  }

  # Service-specific tags
  service_tags = merge(local.common_tags, {
    Component = "service"
  })

  database_tags = merge(local.common_tags, {
    Component = "database"
  })

  storage_tags = merge(local.common_tags, {
    Component = "storage"
  })
}