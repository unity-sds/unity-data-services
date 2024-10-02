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

resource "aws_security_group" "unity_cumulus_lambda_sg" {
  count  = local.security_group_ids_set ? 0 : 1
  vpc_id = var.cumulus_lambda_vpc_id
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = var.tags
}

data "aws_iam_policy_document" "mock_daac_lambda_assume_role_policy" {
  statement {
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}


# IAM Role for Lambda Function
resource "aws_iam_role" "mock_daac_lambda_role" {
  name = "${var.prefix}-mock_daac_lambda_role"
  permissions_boundary = "arn:aws:iam::${local.account_id}:policy/mcp-tenantOperator-AMI-APIG"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}


# IAM Policy for accessing S3 and SNS in other accounts
resource "aws_iam_policy" "mock_daac_lambda_policy" {
  name        = "${var.prefix}-mock_daac_lambda_policy"
  description = "IAM policy for Lambda to access S3 bucket and publish to SNS topic in another account"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "ec2:DescribeNetworkInterfaces",
          "ec2:CreateNetworkInterface",
          "ec2:DeleteNetworkInterface",
          "ec2:DescribeInstances",
          "ec2:AttachNetworkInterface",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams",
          "logs:CreateLogStream",
          "logs:CreateLogGroup",
        ],
        "Resource": "*"
      },
      {
        Effect = "Allow",
        Action = [
          "s3:GetObject*",
          "s3:PutObject"
        ],
        Resource = ["arn:aws:s3:::uds-sbx-cumulus-staging", "arn:aws:s3:::uds-sbx-cumulus-staging/*", "arn:aws:s3:::*unity*/*", "arn:aws:s3:::*unity*/*"]
      },
      {
        Effect = "Allow",
        Action = [
          "sns:Publish"
        ],
        Resource = "arn:aws:sns:${var.uds_region}:${var.uds_account}:${var.uds_prefix}-daac_archiver_response"
      }
    ]
  })
}

# Attach policy to the role
resource "aws_iam_role_policy_attachment" "mock_daac_lambda_policy_attachment" {
  role       = aws_iam_role.mock_daac_lambda_role.name
  policy_arn = aws_iam_policy.mock_daac_lambda_policy.arn
}


resource "aws_lambda_function" "mock_daac_lambda" {
  filename      = local.lambda_file_name
  source_code_hash = filebase64sha256(local.lambda_file_name)
  function_name = "${var.prefix}-mock_daac_lambda"
  role          = aws_iam_role.mock_daac_lambda_role.arn
  handler       = "cumulus_lambda_functions.mock_daac.lambda_function.lambda_handler"
  runtime       = "python3.9"
  timeout       = 300
  environment {
    variables = {
      LOG_LEVEL = var.log_level
      NO_RESPONSE_PERC = var.no_response_perc
      FAIL_PERC = var.no_response_perc
      FAIL_PERC = var.fail_perc
      UDS_ARCHIVE_SNS_TOPIC_ARN = "arn:aws:sns:${var.uds_region}:${var.uds_account}:${var.uds_prefix}-daac_archiver_response"
    }
  }

  vpc_config {
    subnet_ids         = var.cumulus_lambda_subnet_ids
    security_group_ids = local.security_group_ids_set ? var.security_group_ids : [aws_security_group.unity_cumulus_lambda_sg[0].id]
  }
  tags = var.tags
}

resource "aws_sns_topic" "mock_daac_cnm_sns" {
  name = "${var.prefix}-mock_daac_cnm_sns"
  tags = var.tags
}

resource "aws_sns_topic_policy" "granules_cnm_ingester_policy" {
  arn = aws_sns_topic.mock_daac_cnm_sns.arn
  policy = templatefile("${path.module}/mock_daac_sns_policy.json", {
    region: var.aws_region,
    accountId: local.account_id,
    snsName: "${var.prefix}-mock_daac_cnm_sns",
    prefix: var.prefix,

    uds_region: var.uds_region,
    uds_accountId: var.uds_account,
    uds_prefix: var.uds_prefix,
  })
}

resource "aws_sns_topic_subscription" "mock_daac_cnm_sns" { // https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sns_topic_subscription
  topic_arn = aws_sns_topic.mock_daac_cnm_sns.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.mock_daac_lambda.arn
#  filter_policy_scope = "MessageBody"  // MessageAttributes. not using attributes
#  filter_policy = templatefile("${path.module}/ideas_api_job_results_filter_policy.json", {})
}

resource "aws_lambda_permission" "kinesis_fallback" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.mock_daac_lambda.arn
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.mock_daac_cnm_sns.arn
}