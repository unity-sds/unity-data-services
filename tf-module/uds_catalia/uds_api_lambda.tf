resource "aws_lambda_function" "uds_api_1" {
  filename      = local.lambda_file_name
  source_code_hash = filebase64sha256(local.lambda_file_name)
  function_name = "${var.prefix}-uds_api_1"
  role          = local.lambda_role_arn
  handler       = "cumulus_lambda_functions.catalya_uds_api.web_service.handler"
  runtime       = "python3.9"
  timeout       = 300
  memory_size   = 512
  environment {
    variables = {
      LOG_LEVEL = var.log_level
      CATALYA_STATUS_DB = aws_dynamodb_table.uds_ctla_daac_status.name
      CATALYA_DB_NAME = aws_dynamodb_table.uds_ctla_auth_ddb.name
      CATALYA_DAAC_AGREEMENT_DB_NAME = aws_dynamodb_table.uds_ctla_daac_handshake.name
      ADMIN_COMMA_SEP_GROUPS = var.comma_separated_admin_groups
      CATALYA_UDS_STAGING_BUCKET = var.uds_ctla_s3_staging_bucket
      SFA_AUTH = aws_ssm_parameter.daac_archiver_credentials.id
#      UNITY_DEFAULT_PROVIDER = var.unity_default_provider
      COLLECTION_CREATION_LAMBDA_NAME = "arn:aws:lambda:${var.aws_region}:${local.account_id}:function:${var.prefix}-uds_api_1"
#      SNS_TOPIC_ARN = var.cnm_sns_topic_arn
      DAAC_SNS_TOPIC_ARN = aws_sns_topic.uds_daac_archiver_response.arn
      DAPA_API_PREIFX_KEY = var.dapa_api_prefix
      CORS_ORIGINS = var.cors_origins
      UDS_BASE_URL = var.uds_base_url
#      ES_URL = aws_elasticsearch_domain.uds-es.endpoint
#      ES_PORT = 443
#      REPORT_TO_EMS = var.report_to_ems
      DAPA_API_URL_BASE = "${var.uds_base_url}/${var.dapa_api_prefix}"
    }
  }

  vpc_config {
    subnet_ids         = var.cumulus_lambda_subnet_ids
    security_group_ids = local.security_group_ids_set ? var.security_group_ids : [data.aws_security_group.uds_lambda_sg_no_ingress_all_egress.id]
  }
  tags = var.tags
}

resource "aws_lambda_function" "uds_api_authorizer" {
  filename      = local.lambda_file_name
  source_code_hash = filebase64sha256(local.lambda_file_name)
  function_name = "${var.prefix}-uds_api_authorizer"
  role          = local.lambda_role_arn
  handler       = "cumulus_lambda_functions.catalya_uds_api.web_service.handler"
  runtime       = "python3.9"
  timeout       = 300
  memory_size   = 512
  environment {
    variables = {
      LOG_LEVEL = var.log_level
    }
  }

  vpc_config {
    subnet_ids         = var.cumulus_lambda_subnet_ids
    security_group_ids = local.security_group_ids_set ? var.security_group_ids : [data.aws_security_group.uds_lambda_sg_no_ingress_all_egress.id]
  }
  tags = var.tags
}
