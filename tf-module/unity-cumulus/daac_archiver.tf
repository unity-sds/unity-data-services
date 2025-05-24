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
  memory_size   = 256
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

module "daac_archiver_response" {
  source = "./sqs--sns-lambda-connector"

  account_id                 = local.account_id
  lambda_arn                 = aws_lambda_function.daac_archiver_response.arn
  lambda_processing_role_arn = var.lambda_processing_role_arn
  name                       = "daac_archiver_response"
  prefix                     = var.prefix
  sns_arn                    = aws_sns_topic.daac_archiver_response.arn
}