variable "prefix" {
  type = string
}
variable "aws_region" {
  type    = string
  default = "us-west-2"
}

variable "account_id" {
  type = string
  description = "AWS Account ID"
}

variable "tags" {
  description = "Tags to be applied to Cumulus resources that support tags"
  type        = map(string)
  default     = {}
}
variable "cumulus_lambda_vpc_id" {
  type = string
}
variable "security_group_ids" {
  description = "Security Group IDs for Lambdas"
  type        = list(string)
  default     = null
}
variable "cumulus_lambda_subnet_ids" {
  description = "Subnet IDs for Lambdas"
  type        = list(string)
  default     = null
}
