resource "aws_lambda_function" "granules_cnm_ingester" {
  filename      = local.lambda_file_name
  source_code_hash = filebase64sha256(local.lambda_file_name)
  function_name = "${var.prefix}-granules_cnm_ingester"
  role          = var.lambda_processing_role_arn
  handler       = "cumulus_lambda_functions.granules_cnm_ingester.lambda_function.lambda_handler"
  runtime       = "python3.9"
  timeout       = 300
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

data "aws_sns_topic" "granules_cnm_response_topic" {  // https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sns_topic.html
  name              = var.granules_cnm_response_topic
}

resource "aws_sqs_queue" "granules_cnm_response_writer" {  // https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sqs_queue
  name                      = "${var.prefix}-granules_cnm_response_writer"
  delay_seconds             = 0
  max_message_size          = 262144
  message_retention_seconds = 345600
  visibility_timeout_seconds = var.granules_cnm_ingester__sqs_visibility_timeout_seconds  // Used as cool off time in seconds. It will wait for 5 min if it fails
  receive_wait_time_seconds = 0
  policy = templatefile("${path.module}/sqs_policy.json", {
    region: var.aws_region,
    roleArn: var.lambda_processing_role_arn,
    accountId: local.account_id,
    sqsName: "${var.prefix}-granules_cnm_response_writer",
  })
  tags = var.tags
}

resource "aws_sns_topic_subscription" "granules_cnm_response_writer_subscription" { // https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sns_topic_subscription
  topic_arn = data.aws_sns_topic.granules_cnm_response_topic.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.granules_cnm_response_writer.arn
#  filter_policy_scope = "MessageBody"  // MessageAttributes. not using attributes
#  filter_policy = templatefile("${path.module}/ideas_api_job_results_filter_policy.json", {})
}

resource "aws_lambda_event_source_mapping" "granules_cnm_response_writer_lambda_trigger" {  // https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_event_source_mapping#sqs
  event_source_arn = aws_sqs_queue.granules_cnm_response_writer.arn
  function_name    = aws_lambda_function.granules_cnm_response_writer.arn
  batch_size = 1
  enabled = true
}