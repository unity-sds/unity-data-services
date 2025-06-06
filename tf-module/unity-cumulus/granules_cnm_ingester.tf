resource "aws_lambda_function" "granules_cnm_ingester" {
  filename      = local.lambda_file_name
  source_code_hash = filebase64sha256(local.lambda_file_name)
  function_name = "${var.prefix}-granules_cnm_ingester"
  role          = var.lambda_processing_role_arn
  handler       = "cumulus_lambda_functions.granules_cnm_ingester.lambda_function.lambda_handler"
  runtime       = "python3.9"
  timeout       = 300
  memory_size   = 512
  reserved_concurrent_executions = var.granules_cnm_ingester__lambda_concurrency  # TODO
  environment {
    variables = {
      LOG_LEVEL = var.log_level
      SNS_TOPIC_ARN = var.cnm_sns_topic_arn
      ES_URL = aws_elasticsearch_domain.uds-es.endpoint
      ES_PORT = 443
      CUMULUS_WORKFLOW_SQS_URL = var.workflow_sqs_url
      CUMULUS_LAMBDA_PREFIX = var.prefix
      REPORT_TO_EMS = var.report_to_ems
      CUMULUS_WORKFLOW_NAME = "CatalogGranule"
      UNITY_DEFAULT_PROVIDER = var.unity_default_provider
      COLLECTION_CREATION_LAMBDA_NAME = "NA"
    }
  }

  vpc_config {
    subnet_ids         = var.cumulus_lambda_subnet_ids
    security_group_ids = local.security_group_ids_set ? var.security_group_ids : [aws_security_group.unity_cumulus_lambda_sg[0].id]
  }
  tags = var.tags
}

resource "aws_sns_topic" "granules_cnm_ingester" {
  name = "${var.prefix}-granules_cnm_ingester"
  tags = var.tags
}

resource "aws_sns_topic_policy" "granules_cnm_ingester_policy" {
  arn = aws_sns_topic.granules_cnm_ingester.arn
  policy = templatefile("${path.module}/sns_policy.json", {
    region: var.aws_region,
    accountId: local.account_id,
    snsName: "${var.prefix}-granules_cnm_ingester",
    s3Glob: var.granules_cnm_ingester__s3_glob
  })
}


module "granules_cnm_ingester" {
  source = "./sqs--sns-lambda-connector"

  account_id                 = local.account_id
  lambda_arn                 = aws_lambda_function.granules_cnm_ingester.arn
  lambda_processing_role_arn = var.lambda_processing_role_arn
  name                       = "granules_cnm_ingester"
  prefix                     = var.prefix
  sns_arn                    = aws_sns_topic.granules_cnm_ingester.arn
}

################# << CNM Response Writer >> ########################

resource "aws_lambda_function" "granules_cnm_response_writer" {
  filename      = local.lambda_file_name
  source_code_hash = filebase64sha256(local.lambda_file_name)
  function_name = "${var.prefix}-granules_cnm_response_writer"
  role          = var.lambda_processing_role_arn
  handler       = "cumulus_lambda_functions.granules_cnm_response_writer.lambda_function.lambda_handler"
  runtime       = "python3.9"
  timeout       = 300
  memory_size   = 256
  reserved_concurrent_executions = var.granules_cnm_response_writer__lambda_concurrency  # TODO
  environment {
    variables = {
      LOG_LEVEL = var.log_level
      SNS_TOPIC_ARN = var.cnm_sns_topic_arn
    }
  }

  vpc_config {
    subnet_ids         = var.cumulus_lambda_subnet_ids
    security_group_ids = local.security_group_ids_set ? var.security_group_ids : [aws_security_group.unity_cumulus_lambda_sg[0].id]
  }
  tags = var.tags
}

#data "aws_sns_topic" "granules_cnm_response_topic" {  // https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sns_topic.html
#  name              = var.granules_cnm_response_topic
#}

module "granules_cnm_response_writer" {
  source = "./sqs--sns-lambda-connector"

  account_id                 = local.account_id
  lambda_arn                 = aws_lambda_function.granules_cnm_response_writer.arn
  lambda_processing_role_arn = var.lambda_processing_role_arn
  name                       = "granules_cnm_response_writer"
  prefix                     = var.prefix
#  sns_arn                    = data.aws_sns_topic.granules_cnm_response_topic.arn
  sns_arn                    = var.granules_cnm_response_topic
}
