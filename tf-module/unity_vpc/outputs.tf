output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr_block" {
  description = "Primary CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "vpc_secondary_cidr_block" {
  description = "Secondary CIDR block of the VPC"
  value       = aws_vpc_ipv4_cidr_block_association.secondary.cidr_block
}

output "internet_gateway_id" {
  description = "ID of the Internet Gateway"
  value       = aws_internet_gateway.main.id
}

output "nat_gateway_id" {
  description = "ID of the NAT Gateway"
  value       = aws_nat_gateway.main.id
}

output "nat_gateway_public_ip" {
  description = "Public IP address of the NAT Gateway"
  value       = aws_eip.nat.public_ip
}

output "nat_gateway_subnet_id" {
  description = "ID of the NAT Gateway subnet"
  value       = aws_subnet.nat_gateway.id
}

output "public_subnet_ids" {
  description = "List of IDs of public subnets"
  value       = aws_subnet.public[*].id
}

output "public_subnet_cidrs" {
  description = "List of CIDR blocks of public subnets"
  value       = aws_subnet.public[*].cidr_block
}

output "private_subnet_ids" {
  description = "List of IDs of private subnets"
  value       = aws_subnet.private[*].id
}

output "private_subnet_cidrs" {
  description = "List of CIDR blocks of private subnets"
  value       = aws_subnet.private[*].cidr_block
}

output "public_route_table_ids" {
  description = "List of IDs of public route tables"
  value       = aws_route_table.public[*].id
}

output "private_route_table_ids" {
  description = "List of IDs of private route tables"
  value       = aws_route_table.private[*].id
}

output "s3_vpc_endpoint_id" {
  description = "ID of the S3 VPC endpoint"
  value       = aws_vpc_endpoint.s3.id
}

output "vpc_endpoints_security_group_id" {
  description = "ID of the security group for VPC endpoints"
  value       = var.enable_interface_endpoints ? aws_security_group.vpc_endpoints[0].id : null
}

output "execute_api_vpc_endpoint_id" {
  description = "ID of the Execute API VPC endpoint"
  value       = var.enable_interface_endpoints ? aws_vpc_endpoint.execute_api[0].id : null
}

output "efs_vpc_endpoint_id" {
  description = "ID of the EFS VPC endpoint"
  value       = var.enable_interface_endpoints ? aws_vpc_endpoint.efs[0].id : null
}
