variable "prefix" {
  type = string
}
variable "aws_region" {
  type    = string
  default = "us-west-2"
}
variable "tags" {
  description = "Tags to be applied to Cumulus resources that support tags"
  type        = map(string)
  default     = {}
}

variable "cumulus_lambda_vpc_id" {
  description = "VPC ID."
  type = string
}

variable "subnet_ids" {
  description = "subnet IDs for Lambdas"
  type        = list(string)
  default     = null
}

variable "ami_id" {
  description = "The AMI ID for the EC2 instance"
  type        = string
}

variable "instance_type" {
  description = "The type of EC2 instance"
  default = "t3.medium"
  type        = string
}


variable "github_image_url" {
  description = "The full URL of the public Docker image on GitHub (e.g., ghcr.io/user/repo)"
  default = "ghcr.io/unity-sds/unity-data-services"
  type        = string
}

variable "image_tag" {
  description = "The tag of the image to pull from GitHub"
  type        = string
}

variable "shared_services_ec2_subnet_cidr" {
  type = string
  description = "CIDR of the Subnet where Shared Services EC2 resides. This is to allow connections from Shared services to ALB. Example: 10.52.0.0/16"
}

variable "alb_subnet_cidr" {
  type        = string
  description = "CIDR of the Subnet where ALB resides. This is to allow connections from ALB to Stac Browser EC2. Example: 10.52.0.0/16"
}

variable "dapa_api_url_base_val" {
  type = string
  description = "Base URL to hit Stac API to retrieve catalog and so on.. It must start with https and must include the prefix such as `/am-uds-dapa` example: https://d3vc8w9zcq658.cloudfront.net/am-uds-dapa."
}