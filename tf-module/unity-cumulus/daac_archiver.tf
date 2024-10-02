#resource "aws_lambda_function" "daac_archiver_request" {
#  filename      = local.lambda_file_name
#  source_code_hash = filebase64sha256(local.lambda_file_name)
#  function_name = "${var.prefix}-daac_archiver_request"
#  role          = var.lambda_processing_role_arn
#  handler       = "cumulus_lambda_functions.daac_archiver.lambda_function.lambda_handler_request"
#  runtime       = "python3.9"
#  timeout       = 300
#  environment {
#    variables = {
#      LOG_LEVEL = var.log_level
#      ES_URL = aws_elasticsearch_domain.uds-es.endpoint
#      ES_PORT = 443
#    }
#  }
#
#  vpc_config {
#    subnet_ids         = var.cumulus_lambda_subnet_ids
#    security_group_ids = local.security_group_ids_set ? var.security_group_ids : [aws_security_group.unity_cumulus_lambda_sg[0].id]
#  }
#  tags = var.tags
#}

#resource "aws_lambda_event_source_mapping" "daac_archiver_request_lambda_trigger" {  // https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_event_source_mapping#sqs
#  event_source_arn = aws_sqs_queue.granules_cnm_response_writer.arn
#  function_name    = aws_lambda_function.daac_archiver_request.arn
#  batch_size = 1
#  enabled = true
#}

#########################################

resource "aws_lambda_function" "daac_archiver_response" {
  filename      = local.lambda_file_name
  source_code_hash = filebase64sha256(local.lambda_file_name)
  function_name = "${var.prefix}-daac_archiver_response"
  role          = var.lambda_processing_role_arn
  handler       = "cumulus_lambda_functions.daac_archiver.lambda_function.lambda_handler_response"
  runtime       = "python3.9"
  timeout       = 300
  environment {
    variables = {
      LOG_LEVEL = var.log_level
      ES_URL = aws_elasticsearch_domain.uds-es.endpoint
      ES_PORT = 443
    }
  }

  vpc_config {
    subnet_ids         = var.cumulus_lambda_subnet_ids
    security_group_ids = local.security_group_ids_set ? var.security_group_ids : [aws_security_group.unity_cumulus_lambda_sg[0].id]
  }
  tags = var.tags
}


resource "aws_sns_topic" "daac_archiver_response" {
  name = "${var.prefix}-daac_archiver_response"
  tags = var.tags
  // TODO add access policy to be pushed from DAAC / other AWS account
}

resource "aws_sns_topic_policy" "daac_archiver_response_policy" {
  arn = aws_sns_topic.daac_archiver_response.arn
  policy = templatefile("${path.module}/daac_archiver_sns_policy.json", {
    region: var.aws_region,
    accountId: local.account_id,
    snsName: "${var.prefix}-daac_archiver_response",
  })
}

resource "aws_sqs_queue" "daac_archiver_response" {  // https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sqs_queue
  name                      = "${var.prefix}-daac_archiver_response"
  delay_seconds             = 0
  max_message_size          = 262144
  message_retention_seconds = 345600
  visibility_timeout_seconds = var.granules_cnm_ingester__sqs_visibility_timeout_seconds  // Used as cool off time in seconds. It will wait for 5 min if it fails
  receive_wait_time_seconds = 0
  policy = templatefile("${path.module}/sqs_policy.json", {
    region: var.aws_region,
    roleArn: var.lambda_processing_role_arn,
    accountId: local.account_id,
    sqsName: "${var.prefix}-daac_archiver_response",
  })
  tags = var.tags
}

resource "aws_sns_topic_subscription" "daac_archiver_response_subscription" { // https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sns_topic_subscription
  topic_arn = aws_sns_topic.daac_archiver_response.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.daac_archiver_response.arn
#  filter_policy_scope = "MessageBody"  // MessageAttributes. not using attributes
#  filter_policy = templatefile("${path.module}/ideas_api_job_results_filter_policy.json", {})
}


resource "aws_lambda_event_source_mapping" "daac_archiver_response_queue_lambda_trigger" {  // https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_event_source_mapping#sqs
  event_source_arn = aws_sqs_queue.daac_archiver_response.arn
  function_name    = aws_lambda_function.daac_archiver_response.arn
  batch_size = 1
  enabled = true
}