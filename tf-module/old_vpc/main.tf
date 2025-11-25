terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr_block
  enable_dns_hostnames = true
  enable_dns_support   = true
  instance_tenancy     = "default"

  tags = merge(
    var.common_tags,
    {
      Name = "${var.name_prefix}-VPC"
    }
  )
}

# Secondary CIDR Block
resource "aws_vpc_ipv4_cidr_block_association" "secondary" {
  vpc_id     = aws_vpc.main.id
  cidr_block = var.secondary_cidr_block
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = merge(
    var.common_tags,
    {
      Name = "${var.name_prefix}-IGW"
    }
  )
}

# Elastic IP for NAT Gateway
resource "aws_eip" "nat" {
  domain = "vpc"

  tags = merge(
    var.common_tags,
    {
      Name = "${var.name_prefix}-NAT-EIP"
    }
  )

  depends_on = [aws_internet_gateway.main]
}

# NAT Gateway Subnet (small subnet for NAT Gateway)
resource "aws_subnet" "nat_gateway" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.nat_gateway_subnet_cidr
  availability_zone       = var.availability_zones[0]
  map_public_ip_on_launch = true

  tags = merge(
    var.common_tags,
    {
      Name = "${var.name_prefix}-NAT-Gateway-Subnet"
    }
  )
}

# NAT Gateway
resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.nat_gateway.id

  tags = merge(
    var.common_tags,
    {
      Name = "${var.name_prefix}-NAT"
    }
  )

  depends_on = [aws_internet_gateway.main]
}

# Public Subnets
resource "aws_subnet" "public" {
  count = length(var.public_subnet_cidrs)

  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = merge(
    var.common_tags,
    {
      Name = "${var.name_prefix}-Pub-Subnet-${count.index + 1}"
    }
  )
}

# Private Subnets
resource "aws_subnet" "private" {
  count = length(var.private_subnet_cidrs)

  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = merge(
    var.common_tags,
    {
      Name = "${var.name_prefix}-Priv-Subnet-${count.index + 1}"
    }
  )
}

# Route Table for NAT Gateway Subnet
resource "aws_route_table" "nat_gateway" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = merge(
    var.common_tags,
    {
      Name    = "${var.name_prefix}-NAT-Gateway-RT"
      Network = "Public"
    }
  )
}

resource "aws_route_table_association" "nat_gateway" {
  subnet_id      = aws_subnet.nat_gateway.id
  route_table_id = aws_route_table.nat_gateway.id
}

# Public Route Tables (one per AZ)
resource "aws_route_table" "public" {
  count = length(var.public_subnet_cidrs)

  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = merge(
    var.common_tags,
    {
      Name    = "${var.name_prefix}-Public-RT-AZ${count.index + 1}"
      Network = "Public AZ${count.index + 1}"
    }
  )
}

resource "aws_route_table_association" "public" {
  count = length(var.public_subnet_cidrs)

  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public[count.index].id
}

# Private Route Tables (one per AZ)
resource "aws_route_table" "private" {
  count = length(var.private_subnet_cidrs)

  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main.id
  }

  tags = merge(
    var.common_tags,
    {
      Name    = "${var.name_prefix}-Private-RT-AZ${count.index + 1}"
      Network = "Private AZ${count.index + 1}"
    }
  )
}

resource "aws_route_table_association" "private" {
  count = length(var.private_subnet_cidrs)

  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}

# S3 VPC Endpoint (Gateway)
resource "aws_vpc_endpoint" "s3" {
  vpc_id       = aws_vpc.main.id
  service_name = "com.amazonaws.${var.aws_region}.s3"

  route_table_ids = concat(
    aws_route_table.public[*].id,
    aws_route_table.private[*].id
  )

  tags = merge(
    var.common_tags,
    {
      Name = "${var.name_prefix}-s3-endpoint"
    }
  )
}

# VPC Endpoints for Interface services (optional, can be enabled via variable)
resource "aws_security_group" "vpc_endpoints" {
  count = var.enable_interface_endpoints ? 1 : 0

  name        = "${var.name_prefix}-vpc-endpoints-sg"
  description = "Security group for VPC endpoints"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr_block, var.secondary_cidr_block]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.common_tags,
    {
      Name = "${var.name_prefix}-vpc-endpoints-sg"
    }
  )
}

# Execute API VPC Endpoint
resource "aws_vpc_endpoint" "execute_api" {
  count = var.enable_interface_endpoints ? 1 : 0

  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.aws_region}.execute-api"
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = false

  subnet_ids = slice(aws_subnet.private[*].id, 0, min(2, length(aws_subnet.private)))

  security_group_ids = [aws_security_group.vpc_endpoints[0].id]

  tags = merge(
    var.common_tags,
    {
      Name = "${var.name_prefix}-execute-api-endpoint"
    }
  )
}

# EFS VPC Endpoint
resource "aws_vpc_endpoint" "efs" {
  count = var.enable_interface_endpoints ? 1 : 0

  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.aws_region}.elasticfilesystem-fips"
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = false

  subnet_ids = aws_subnet.private[*].id

  security_group_ids = [aws_security_group.vpc_endpoints[0].id]

  tags = merge(
    var.common_tags,
    {
      Name = "${var.name_prefix}-efs-endpoint"
    }
  )
}
