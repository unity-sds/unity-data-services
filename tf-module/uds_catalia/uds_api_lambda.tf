resource "aws_lambda_function" "uds_api_1" {
  filename      = local.lambda_file_name
  source_code_hash = filebase64sha256(local.lambda_file_name)
  function_name = "${var.prefix}-uds_api_1"
  role          = local.lambda_role_arn
  handler       = "cumulus_lambda_functions.catalya_uds_api.web_service.handler"
  runtime       = local.lambda_python_runtime
  timeout       = 300
  memory_size   = 512
  environment {
    variables = {
      LOG_LEVEL = var.log_level
      UDS_API_CREDS = aws_ssm_parameter.uds_api_credentials.id
      CATALYA_STATUS_DB = aws_dynamodb_table.uds_ctla_daac_status.name
      CATALYA_TRACING_DB = aws_dynamodb_table.uds_ctla_archiving_traces.name
      CATALYA_DB_NAME = aws_dynamodb_table.uds_ctla_auth_ddb.name
      CATALYA_DAAC_AGREEMENT_DB_NAME = aws_dynamodb_table.uds_ctla_daac_handshake.name
      ADMIN_COMMA_SEP_GROUPS = var.comma_separated_admin_groups
      CATALYA_UDS_STAGING_BUCKET = var.uds_ctla_s3_staging_bucket
      SFA_AUTH = aws_ssm_parameter.daac_archiver_credentials.id
#      UNITY_DEFAULT_PROVIDER = var.unity_default_provider
      ARCHIVE_LAMBDA_NAME = "arn:aws:lambda:${var.aws_region}:${local.account_id}:function:${var.prefix}-uds_api_1"
#      SNS_TOPIC_ARN = var.cnm_sns_topic_arn
      DAPA_API_PREIFX_KEY = var.dapa_api_prefix
      CORS_ORIGINS = var.cors_origins
      DAPA_API_URL_BASE = "${var.uds_base_url}/${var.dapa_api_prefix}"
      FARGATE_CONFIG = aws_ssm_parameter.daac_archiver_fargate_config.id

      CNM_PLUG_IN_NAMES = var.CNM_PLUG_IN_NAMES
      CNM_STORAGE_CLASS = var.CNM_STORAGE_CLASS
      CNM_STORAGE_BUCKET = var.CNM_STORAGE_BUCKET
      CNM_STORAGE_PREFIX = var.CNM_STORAGE_PREFIX
      CATALYA_RDS_CREDS = var.CATALYA_RDS_CREDS_PARAM_PATH
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
  handler       = "cumulus_lambda_functions.keycloak_authorizer.lambda_function.lambda_handler"
  runtime       = local.lambda_python_runtime
  timeout       = 300
  memory_size   = 512
  environment {
    variables = {
      UDS_API_CREDS = aws_ssm_parameter.uds_api_credentials.id
      LOG_LEVEL = var.log_level
    }
  }

  vpc_config {
    subnet_ids         = var.cumulus_lambda_subnet_ids
    security_group_ids = local.security_group_ids_set ? var.security_group_ids : [data.aws_security_group.uds_lambda_sg_no_ingress_all_egress.id]
  }
  tags = var.tags
}
