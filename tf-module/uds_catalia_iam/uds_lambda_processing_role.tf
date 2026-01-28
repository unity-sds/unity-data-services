variable "lambda_role_arn" {
  description = "Optional pre-existing Lambda role ARN"
  type        = string
  default     = null
}

variable "create_lambda_role" {
  description = "Whether Terraform should create the IAM role"
  type        = bool
  default     = false
}

locals {
  all_bucket_names       = [for k, v in var.buckets : v.name]
  ddb_tbl_arns = ["arn:aws:dynamodb:${var.aws_region}:${var.account_id}:table/${var.prefix}*"]
  lambda_role_arn =aws_iam_role.lambda_processing.arn
#  lambda_role_arn = var.create_lambda_role ? aws_iam_role.lambda_processing.arn : var.lambda_role_arn
}

resource "aws_iam_role" "lambda_processing" {
#  count = var.create_lambda_role ? 1 : 0
  name                 = "${var.prefix}-lambda-processing"
  assume_role_policy   = data.aws_iam_policy_document.lambda_assume_role_policy.json
  permissions_boundary = var.permissions_boundary_arn
  tags                 = var.tags
}
data "aws_iam_policy_document" "lambda_processing_policy" {
  statement {
    actions = [
      "ec2:CreateNetworkInterface",
      "sns:publish",
      "cloudformation:DescribeStacks",
      "dynamodb:ListTables",
      "ec2:DeleteNetworkInterface",
      "ec2:DescribeNetworkInterfaces",
      "events:DeleteRule",
      "events:DescribeRule",
      "events:DisableRule",
      "events:EnableRule",
      "events:ListRules",
      "events:PutRule",
      "kinesis:DescribeStream",
      "kinesis:GetRecords",
      "kinesis:GetShardIterator",
      "kinesis:ListStreams",
      "kinesis:PutRecord",
      "lambda:GetFunction",
      "lambda:invokeFunction",
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:DescribeLogStreams",
      "logs:PutLogEvents",
      "s3:ListAllMyBuckets",
      "sns:List*",
      "states:DescribeActivity",
      "states:DescribeExecution",
      "states:GetActivityTask",
      "states:GetExecutionHistory",
      "states:ListStateMachines",
      "states:SendTaskFailure",
      "states:SendTaskSuccess",
      "states:StartExecution",
      "states:StopExecution"
    ]
    resources = ["*"]
  }

  statement {
    actions = [
      "s3:GetAccelerateConfiguration",
      "s3:GetLifecycleConfiguration",
      "s3:GetReplicationConfiguration",
      "s3:GetBucket*",
      "s3:PutAccelerateConfiguration",
      "s3:PutLifecycleConfiguration",
      "s3:PutReplicationConfiguration",
      "s3:PutBucket*",
      "s3:ListBucket*",
    ]
    resources = [for b in local.all_bucket_names : "arn:aws:s3:::${b}"]
  }

  statement {
    actions = [
      "s3:AbortMultipartUpload",
      "s3:GetObject*",
      "s3:PutObject*",
      "s3:ListMultipartUploadParts",
      "s3:DeleteObject",
      "s3:DeleteObjectVersion",
    ]
    resources = [for b in local.all_bucket_names : "arn:aws:s3:::${b}/*"]
  }

  statement {
    actions = [
      "dynamodb:DeleteItem",
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:Scan",
      "dynamodb:UpdateItem",
      "dynamodb:BatchWriteItem",
      "dynamodb:UpdateContinuousBackups",
      "dynamodb:DescribeContinuousBackups",
    ]
    resources = local.ddb_tbl_arns
  }

  statement {
    actions   = ["dynamodb:Query"]
    resources = local.ddb_tbl_arns
  }

  statement {
    actions = [
      "dynamodb:GetRecords",
      "dynamodb:GetShardIterator",
      "dynamodb:DescribeStream",
      "dynamodb:ListStreams",
    ]
    resources = local.ddb_tbl_arns
  }

  statement {
    actions = [
      "sqs:SendMessage",
      "sqs:ReceiveMessage",
      "sqs:ChangeMessageVisibility",
      "sqs:DeleteMessage",
      "sqs:GetQueueUrl",
      "sqs:GetQueueAttributes",
    ]
    resources = ["arn:aws:sqs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:*"]
  }

  statement {
    actions = [
      "ssm:GetParameter",
      "ssm:GetParameters",
    ]
    resources = ["arn:aws:ssm:${var.aws_region}:${var.account_id}:parameter/${var.prefix}/*"]
  }

#  statement {
#    actions   = ["kms:Decrypt"]
#    resources = [module.archive.provider_kms_key_arn]
#  }
#
#  statement {
#    actions = ["secretsmanager:GetSecretValue"]
#    resources = [
#      module.archive.cmr_password_secret_arn,
#      module.archive.launchpad_passphrase_secret_arn,
#    ]
#  }
}

resource "aws_iam_role_policy" "lambda_processing" {
  name   = "${var.prefix}_lambda_processing_policy"
  role   = aws_iam_role.lambda_processing.id
  policy = data.aws_iam_policy_document.lambda_processing_policy.json
}
#
#data "aws_iam_policy_document" "lambda_assume_role_policy" {
#  statement {
#    actions = ["sts:AssumeRole"]
#    principals {
#      type        = "Service"
#      identifiers = ["lambda.amazonaws.com"]
#    }
#  }
#}

resource "aws_iam_policy" "uds_lambda_processing_policy" {
  name        = "${var.prefix}-uds_lambda_processing_policy"
  description = "IAM policy for Lambda to access S3 bucket and publish to SNS topic in another account"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "sts:AssumeRole",
        ],
        "Resource": "arn:aws:iam::*:role/*"
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "uds_lambda_processing_policy_attachment" {
  role       = aws_iam_role.lambda_processing.name
  policy_arn = aws_iam_policy.uds_lambda_processing_policy.arn
}
