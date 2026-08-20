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

resource "aws_security_group" "uds_lambda_sg_no_ingress_all_egress" {
  name   = "${var.prefix}-uds_lambda_sg_no_ingress_all_egress"
  vpc_id = var.cumulus_lambda_vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    self      = true
  }
  tags = var.tags
}

data "aws_iam_policy_document" "lambda_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}
