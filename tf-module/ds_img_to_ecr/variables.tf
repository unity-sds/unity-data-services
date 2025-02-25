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

variable "github_image_url" {
  description = "The full URL of the public Docker image on GitHub (e.g., ghcr.io/user/repo)"
  default = "ghcr.io/unity-sds/unity-data-services"
  type        = string
}

variable "image_tag" {
  description = "The tag of the image to pull from GitHub"
  type        = string
}

variable "ecr_repo_name" {
  description = "The name of the ECR repository"
  default = "unity-data-services"
  type        = string
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

variable "cumulus_lambda_vpc_id" {
  description = "VPC ID."
  type = string
}
variable "cumulus_subnet_id" {
  description = "subnet group ID where a new EC2 will be placed"
  type = string
}