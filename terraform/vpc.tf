# vpc.tf - Basic VPC for Kubernetes only

# VPC
resource "aws_vpc" "main" {
  count = local.enable_kubernetes ? 1 : 0

  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(local.common_tags, {
    Name = "${local.resource_prefix}-vpc"
  })
}

# Public subnets
resource "aws_subnet" "public" {
  count = local.enable_kubernetes ? 2 : 0

  vpc_id                  = aws_vpc.main[0].id
  cidr_block              = "10.0.${count.index + 1}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = merge(local.common_tags, {
    Name = "${local.resource_prefix}-public-subnet-${count.index + 1}"
    "kubernetes.io/role/elb" = "1"
  })
}

# Private subnets
resource "aws_subnet" "private" {
  count = local.enable_kubernetes ? 2 : 0

  vpc_id            = aws_vpc.main[0].id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = merge(local.common_tags, {
    Name = "${local.resource_prefix}-private-subnet-${count.index + 1}"
    "kubernetes.io/role/internal-elb" = "1"
  })
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  count = local.create_vpc ? 1 : 0

  vpc_id = aws_vpc.main[0].id

  tags = merge(local.common_tags, {
    Name = "${local.resource_prefix}-igw"
  })
}

# NAT Gateway (regular profile only)
resource "aws_eip" "nat" {
  count = local.create_nat ? 1 : 0

  domain = "vpc"

  tags = merge(local.common_tags, {
    Name = "${local.resource_prefix}-nat-eip"
  })

  depends_on = [aws_internet_gateway.main]
}

resource "aws_nat_gateway" "main" {
  count = local.create_nat ? 1 : 0

  allocation_id = aws_eip.nat[0].id
  subnet_id     = aws_subnet.public[0].id

  tags = merge(local.common_tags, {
    Name = "${local.resource_prefix}-nat"
  })

  depends_on = [aws_internet_gateway.main]
}

# Public route table
resource "aws_route_table" "public" {
  count = local.create_vpc ? 1 : 0

  vpc_id = aws_vpc.main[0].id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main[0].id
  }

  tags = merge(local.common_tags, {
    Name = "${local.resource_prefix}-public-rt"
  })
}

# Private route table
resource "aws_route_table" "private" {
  count = local.create_vpc ? 1 : 0

  vpc_id = aws_vpc.main[0].id

  dynamic "route" {
    for_each = local.create_nat ? [1] : []
    content {
      cidr_block     = "0.0.0.0/0"
      nat_gateway_id = aws_nat_gateway.main[0].id
    }
  }

  tags = merge(local.common_tags, {
    Name = "${local.resource_prefix}-private-rt"
  })
}

# Route table associations
resource "aws_route_table_association" "public" {
  count = local.create_vpc ? length(aws_subnet.public) : 0

  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public[0].id
}

resource "aws_route_table_association" "private" {
  count = local.create_vpc ? length(aws_subnet.private) : 0

  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[0].id
}