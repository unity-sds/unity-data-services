variable "aws_region" {
  description = "AWS region where the VPC will be created"
  type        = string
  default     = "us-west-2"
}

variable "name_prefix" {
  description = "Prefix for naming resources"
  type        = string
  default     = "Unity-VPC"
}

variable "vpc_cidr_block" {
  description = "Primary CIDR block for the VPC"
  type        = string
  default     = "10.52.8.0/22"
}

variable "secondary_cidr_block" {
  description = "Secondary CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones to use for subnets"
  type        = list(string)
  default     = ["us-west-2a", "us-west-2b", "us-west-2c", "us-west-2d"]
}

variable "nat_gateway_subnet_cidr" {
  description = "CIDR block for NAT Gateway subnet"
  type        = string
  default     = "10.52.11.0/28"
}

variable "public_subnet_cidrs" {
  description = "List of CIDR blocks for public subnets"
  type        = list(string)
  default = [
    "10.52.8.0/24",   # Public Subnet 01 - AZ1
    "10.52.9.0/24",   # Public Subnet 02 - AZ2
    "10.0.64.0/19",   # Public Subnet 03 - AZ3
    "10.0.96.0/19"    # Public Subnet 04 - AZ4
  ]
}

variable "private_subnet_cidrs" {
  description = "List of CIDR blocks for private subnets"
  type        = list(string)
  default = [
    "10.52.10.0/25",    # Private Subnet 01 - AZ1
    "10.52.10.128/25",  # Private Subnet 02 - AZ2
    "10.0.0.0/19",      # Private Subnet 03 - AZ3
    "10.0.32.0/19"      # Private Subnet 04 - AZ4
  ]
}

variable "enable_interface_endpoints" {
  description = "Enable VPC interface endpoints for AWS services"
  type        = bool
  default     = false
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default = {
    Project = "Unity"
    ManagedBy = "Terraform"
  }
}
