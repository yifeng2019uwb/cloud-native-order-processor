# ===== TWO AZ VPC (Required for EKS/RDS but still cost-optimized) =====
# vpc.tf
resource "aws_vpc" "main" {
  count = local.create_vpc ? 1 : 0

  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.project_name}-${var.environment}-vpc"
  }
}

# Two public subnets (required for EKS)
resource "aws_subnet" "public" {
  count = var.compute_type == "kubernetes" ? var.availability_zones_count : 0

  vpc_id                  = aws_vpc.main[0].id
  cidr_block              = "10.0.${count.index + 1}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = false

  tags = {
    Name                     = "${var.project_name}-${var.environment}-public-subnet-${count.index + 1}"
    "kubernetes.io/role/elb" = "1"
  }
}

# Two private subnets (required for RDS and EKS)
resource "aws_subnet" "private" {
  count = var.compute_type == "kubernetes" ? var.availability_zones_count : 0
  vpc_id = aws_vpc.main[0].id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name                              = "${var.project_name}-${var.environment}-private-subnet-${count.index + 1}"
    "kubernetes.io/role/internal-elb" = "1"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  count = var.compute_type == "kubernetes" ? 1 : 0
  vpc_id = aws_vpc.main[0].id

  tags = {
    Name = "${var.project_name}-${var.environment}-igw"
  }
}

# COST OPTIMIZATION: Single NAT Gateway (not HA but saves 50% NAT costs)
# All private subnets will route through one NAT Gateway in first AZ
resource "aws_eip" "nat" {
  count = local.enable_kubernetes ? 1 : 0
  domain = "vpc"
  tags = {
    Name = "${var.project_name}-${var.environment}-nat-eip"
  }
  depends_on = [aws_internet_gateway.main]
}

resource "aws_nat_gateway" "main" {
  count = local.enable_kubernetes ? 1 : 0
  allocation_id = aws_eip.nat[0].id
  subnet_id     = aws_subnet.public[0].id # Use first public subnet

  tags = {
    Name = "${var.project_name}-${var.environment}-nat"
  }
  depends_on = [aws_internet_gateway.main]
}

# Route Tables
resource "aws_route_table" "public" {
  count = var.compute_type == "kubernetes" ? 1 : 0

  vpc_id = aws_vpc.main[0].id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main[0].id
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-public-rt"
    Type = "public"
  })
}

# Single private route table for both private subnets (cost optimization)
resource "aws_route_table" "private" {
  count = var.compute_type == "kubernetes" ? var.availability_zones_count : 0

  vpc_id = aws_vpc.main[0].id

  dynamic "route" {
    for_each = var.profile == "regular" ? [1] : []
    content {
      cidr_block     = "0.0.0.0/0"
      nat_gateway_id = aws_nat_gateway.main[0].id
    }
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-private-rt"
  }
}

# Associate public subnets with public route table
resource "aws_route_table_association" "public" {
  count = length(aws_subnet.public)

  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public[0].id
}

# Associate both private subnets with single private route table
resource "aws_route_table_association" "private" {
  count = var.compute_type == "kubernetes" ? length(aws_subnet.private) : 0

  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[0].id
}

# VPC Endpoints for minimal/learning (replace NAT Gateway)
resource "aws_vpc_endpoint" "s3" {
  count = var.compute_type == "kubernetes" ? 1 : 0
  vpc_id = aws_vpc.main[0].id  # Add [0]
  service_name = "com.amazonaws.${var.region}.s3"

  tags = {
    Name = "${var.project_name}-${var.environment}-s3-endpoint"
  }
}