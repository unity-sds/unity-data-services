variable "prefix" {
  type = string
}
variable "name" {
  type = string
}
variable "sns_arn" {
  type = string
}
variable "lambda_arn" {
  type = string
}
variable "sqs_batch_size" {
  type = number
  default = 1
}
variable "retried_count" {
  type = number
  default = 3
}
variable "cool_off" {
  type = number
  default = 300
  description = "visibility time out for sqs. in seconds"
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
variable "lambda_processing_role_arn" {
  type = string
}
variable "account_id" {
  type = string
  description = "AWS Account ID"
}