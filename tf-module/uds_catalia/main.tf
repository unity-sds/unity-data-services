 provider "aws" {
  region = var.aws_region
  ignore_tags {
    key_prefixes = ["gsfc-ngap"]
  }
}
data "aws_caller_identity" "current" {}

locals {
  account_id = data.aws_caller_identity.current.account_id
  lambda_file_name = "${path.module}/build/cumulus_lambda_functions_deployment.zip"
  security_group_ids_set = var.security_group_ids != null
  lambda_role_arn = data.aws_iam_role.lambda_processing.arn
  lambda_python_runtime = "python3.9"
}

variable "buckets" {
  description = "Map identifying the buckets for the deployment"
  type        = map(object({ name = string, type = string }))
  default     = {}
}
##    resources = [for k, v in var.dynamo_tables : "${v.arn}/stream/*"]
#variable "dynamo_tables" {
#  type = map(object({ name = string, arn = string }))
#}

data "aws_security_group" "uds_lambda_sg_no_ingress_all_egress" {
  name = "${var.prefix}-uds_lambda_sg_no_ingress_all_egress"
}

data "aws_iam_role" "lambda_processing" {
 #  count = var.create_lambda_role ? 1 : 0
 name = "${var.prefix}-lambda-processing"
}
