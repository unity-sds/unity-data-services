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

resource "aws_lambda_function" "uds_daac_archiver_response" {
  # TODO: Add buffer and retries Also store a copy in S3 ?
  filename      = local.lambda_file_name
  source_code_hash = filebase64sha256(local.lambda_file_name)
  function_name = "${var.prefix}-uds_daac_archiver_response"
  role          = local.lambda_role_arn
  handler       = "cumulus_lambda_functions.daac_archiver.lambda_function.lambda_handler_response"
  runtime       = local.lambda_python_runtime
  timeout       = 300
  memory_size   = 256
  environment {
    variables = {
      LOG_LEVEL = var.log_level
      ARCHIVAL_STATUS_MECHANISM = "CATALYA"  # UDS or FAST_STAC
      SFA_AUTH = aws_ssm_parameter.daac_archiver_credentials.id
      CATALYA_STATUS_DB = aws_dynamodb_table.uds_ctla_daac_status.name
      CATALYA_TRACING_DB = aws_dynamodb_table.uds_ctla_archiving_traces.name
      CNM_PLUG_IN_NAMES = var.CNM_PLUG_IN_NAMES
      CNM_STORAGE_BUCKET = var.CNM_STORAGE_BUCKET
      CNM_STORAGE_PREFIX = var.CNM_STORAGE_PREFIX
    }
  }

  vpc_config {
    subnet_ids         = var.cumulus_lambda_subnet_ids
    security_group_ids = local.security_group_ids_set ? var.security_group_ids : [data.aws_security_group.uds_lambda_sg_no_ingress_all_egress.id]
  }
  tags = var.tags
}

resource "aws_ssm_parameter" "daac_archiver_fargate_config" {
  name  = "/${var.prefix}/daac-archiver/daac_archiver_fargate_config"
  type  = "String"
  value = jsonencode({
    CLUSTER_NAME = aws_ecs_cluster.ds_cluster.name
    TASK_DEFINITION = aws_ecs_task_definition.ds_cluster.arn
    SUBNET_IDs = var.cumulus_lambda_subnet_ids
    SECURITY_GROUPS = local.security_group_ids_set ? var.security_group_ids : [data.aws_security_group.uds_lambda_sg_no_ingress_all_egress.id]  # TODO. Not sure it will work.
    CONTAINER_NAME = "${var.uds_docker_name}:${var.uds_docker_version}"
  })
  description = "Secure credentials and configuration for DAAC archiver service"
  tags        = var.tags
}


resource "aws_ssm_parameter" "daac_archiver_credentials" {
  name  = "/${var.prefix}/daac-archiver/daac_archiver_credentials"
  type  = "SecureString"
  value = jsonencode({
    DS_URL           = "https://dps-stac.dit.maap-project.org/"
#    SFA_USERNAME     = "TODO"
#    SFA_PASSWORD     = "TODO"
#    SFA_AUTH_KEY     = "TODO"
#    SFA_AUTH_VALUE   = "TODO"
#    SFA_BEARER_TOKEN = "TODO"
  })
  description = "Secure credentials and configuration for DAAC archiver service"
  tags        = var.tags
}


resource "aws_ssm_parameter" "uds_api_credentials" {
  name  = "/${var.prefix}/daac-archiver/uds_api_credentials"
  type  = "SecureString"
  value = jsonencode({
    API_BASE_URL = var.UDS_API_BASE_URL
    MAAP_API_HOST = var.MAAP_API_HOST
    DPS_MACHINE_TOKEN = var.DPS_MACHINE_TOKEN
  })
  description = "Secure credentials and configuration for DAAC archiver service"
  tags        = var.tags
}


resource "aws_sns_topic" "uds_daac_archiver_response" {
  name = "${var.prefix}-uds_daac_archiver_response"
  tags = var.tags
  // TODO add access policy to be pushed from DAAC / other AWS account
}

resource "aws_sns_topic_policy" "daac_archiver_response_policy" {
  arn = aws_sns_topic.uds_daac_archiver_response.arn
  policy = templatefile("${path.module}/daac_archiver_sns_policy.json", {
    region: var.aws_region,
    accountId: local.account_id,
    snsName: "${var.prefix}-daac_archiver_response",
  })
}

module "daac_archiver_response" {
  source = "../sqs--sns-lambda-connector"

  account_id                 = local.account_id
  lambda_arn                 = aws_lambda_function.uds_daac_archiver_response.arn
  lambda_processing_role_arn          = local.lambda_role_arn
  name                       = "daac_archiver_response"
  prefix                     = var.prefix
  sns_arn                    = aws_sns_topic.uds_daac_archiver_response.arn
}

resource "aws_lambda_function" "catalya_archiver_trigger" {
  filename      = local.lambda_file_name
  source_code_hash = filebase64sha256(local.lambda_file_name)
  function_name = "${var.prefix}-catalya_archiver_trigger"
  role          = local.lambda_role_arn
  handler       = "cumulus_lambda_functions.catalya_archive_trigger.lambda_function.lambda_handler"
  runtime       = local.lambda_python_runtime
  timeout       = 900
  memory_size   = 10240
  environment {
    variables = {
      LOG_LEVEL = var.log_level
      ARCHIVAL_STATUS_MECHANISM = "CATALYA"  # UDS or FAST_STAC
      SFA_AUTH = aws_ssm_parameter.daac_archiver_credentials.id
      UDS_API_CREDS = aws_ssm_parameter.uds_api_credentials.id
      CATALYA_STATUS_DB = aws_dynamodb_table.uds_ctla_daac_status.name
    }
  }

  vpc_config {
    subnet_ids         = var.cumulus_lambda_subnet_ids
    security_group_ids = local.security_group_ids_set ? var.security_group_ids : [data.aws_security_group.uds_lambda_sg_no_ingress_all_egress.id]
  }
  tags = var.tags
}


# resource "aws_sns_topic" "catalya_archiver_trigger" {
#   name = "${var.prefix}-catalya_archiver_trigger"
#   tags = var.tags
#   // TODO add access policy to be pushed from all MAAP S3 buckets
# }
#
#
#
# resource "aws_sns_topic_policy" "catalya_archiver_trigger" {
#   arn = aws_sns_topic.catalya_archiver_trigger.arn
#   policy = templatefile("${path.module}/daac_archiver_sns_policy.json", {
#     region: var.aws_region,
#     accountId: local.account_id,
#     snsName: "${var.prefix}-catalya_archiver_trigger",
#   })
# }

module "catalya_archiver_trigger" {
  source = "../sqs--sns-lambda-connector"

  account_id                 = local.account_id
  lambda_arn                 = aws_lambda_function.catalya_archiver_trigger.arn
  lambda_processing_role_arn          = local.lambda_role_arn
  name                       = "catalya_archiver_trigger"
  prefix                     = var.prefix
  sns_arn                    =  var.ARCHIVER_TRIGER_SNS_ARN
  cool_off = aws_lambda_function.catalya_archiver_trigger.timeout
}
