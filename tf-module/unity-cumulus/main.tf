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

data "aws_iam_policy_document" "lambda_assume_role_policy" {
  statement {
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_lambda_function" "metadata_s4pa_generate_cmr" {
  filename      = local.lambda_file_name
  source_code_hash = filebase64sha256(local.lambda_file_name)
  function_name = "${var.prefix}-metadata_s4pa_generate_cmr"
  role          = var.lambda_processing_role_arn
  handler       = "cumulus_lambda_functions.metadata_s4pa_generate_cmr.lambda_function.lambda_handler"
  runtime       = "python3.9"
  timeout       = 300
  memory_size   = 256
  environment {
    variables = {
      LOG_LEVEL = var.log_level
      FILE_POSTFIX = var.metadata_s4pa_file_postfix
    }
  }

  vpc_config {
    subnet_ids         = var.cumulus_lambda_subnet_ids
    security_group_ids = local.security_group_ids_set ? var.security_group_ids : [aws_security_group.unity_cumulus_lambda_sg[0].id]
  }
  tags = var.tags
}

resource "aws_lambda_function" "metadata_cas_generate_cmr" {
  filename      = local.lambda_file_name
  source_code_hash = filebase64sha256(local.lambda_file_name)
  function_name = "${var.prefix}-metadata_cas_generate_cmr"
  role          = var.lambda_processing_role_arn
  handler       = "cumulus_lambda_functions.metadata_cas_generate_cmr.lambda_function.lambda_handler"
  runtime       = "python3.9"
  timeout       = 300
  memory_size   = 256
  environment {
    variables = {
      LOG_LEVEL = var.log_level
    }
  }

  vpc_config {
    subnet_ids         = var.cumulus_lambda_subnet_ids
    security_group_ids = local.security_group_ids_set ? var.security_group_ids : [aws_security_group.unity_cumulus_lambda_sg[0].id]
  }
  tags = var.tags
}

resource "aws_lambda_function" "metadata_stac_generate_cmr" {
  filename      = local.lambda_file_name
  source_code_hash = filebase64sha256(local.lambda_file_name)
  function_name = "${var.prefix}-metadata_stac_generate_cmr"
  role          = var.lambda_processing_role_arn
  handler       = "cumulus_lambda_functions.metadata_stac_generate_cmr.lambda_function.lambda_handler"
  runtime       = "python3.9"
  timeout       = 300
  memory_size   = 256
  environment {
    variables = {
      LOG_LEVEL = var.log_level
      FILE_POSTFIX = var.metadata_stac_file_postfix
      VALID_FILETYPE = var.valid_file_type
      REGISTER_CUSTOM_METADATA = var.register_custom_metadata
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

resource "aws_lambda_function" "granules_to_es" {
  filename      = local.lambda_file_name
  source_code_hash = filebase64sha256(local.lambda_file_name)
  function_name = "${var.prefix}-granules_to_es"
  role          = var.lambda_processing_role_arn
  handler       = "cumulus_lambda_functions.granules_to_es.lambda_function.lambda_handler"
  runtime       = "python3.9"
  timeout       = 300
  memory_size   = 256
  environment {
    variables = {
      LOG_LEVEL = var.log_level
      ES_URL = aws_elasticsearch_domain.uds-es.endpoint
      VALID_FILETYPE = var.valid_file_type
      FILE_POSTFIX = var.metadata_stac_file_postfix
      ES_PORT = 443
    }
  }

  vpc_config {
    subnet_ids         = var.cumulus_lambda_subnet_ids
    security_group_ids = local.security_group_ids_set ? var.security_group_ids : [aws_security_group.unity_cumulus_lambda_sg[0].id]
  }
  tags = var.tags
}

resource "aws_lambda_function" "uds_api_1" {
  filename      = local.lambda_file_name
  source_code_hash = filebase64sha256(local.lambda_file_name)
  function_name = "${var.prefix}-uds_api_1"
  role          = var.lambda_processing_role_arn
  handler       = "cumulus_lambda_functions.uds_api.web_service.handler"
  runtime       = "python3.9"
  timeout       = 300
  memory_size   = 512
  environment {
    variables = {
      CUMULUS_BASE = var.cumulus_base
      CUMULUS_LAMBDA_PREFIX = var.prefix
      LOG_LEVEL = var.log_level
      CUMULUS_WORKFLOW_SQS_URL = var.workflow_sqs_url
      CUMULUS_WORKFLOW_NAME = "CatalogGranule"
      UNITY_DEFAULT_PROVIDER = var.unity_default_provider
      COLLECTION_CREATION_LAMBDA_NAME = "arn:aws:lambda:${var.aws_region}:${local.account_id}:function:${var.prefix}-uds_api_1"
      SNS_TOPIC_ARN = var.cnm_sns_topic_arn
      DAAC_SNS_TOPIC_ARN = aws_sns_topic.daac_archiver_response.arn
      DAPA_API_PREIFX_KEY = var.dapa_api_prefix
      CORS_ORIGINS = var.cors_origins
      UDS_BASE_URL = var.uds_base_url
      ES_URL = aws_elasticsearch_domain.uds-es.endpoint
      ES_PORT = 443
      REPORT_TO_EMS = var.report_to_ems
      ADMIN_COMMA_SEP_GROUPS = var.comma_separated_admin_groups
      DAPA_API_URL_BASE = "${var.uds_base_url}/${var.dapa_api_prefix}"
    }
  }

  vpc_config {
    subnet_ids         = var.cumulus_lambda_subnet_ids
    security_group_ids = local.security_group_ids_set ? var.security_group_ids : [aws_security_group.unity_cumulus_lambda_sg[0].id]
  }
  tags = var.tags
}

resource "aws_ssm_parameter" "uds_api_1" {
  name  = "/unity/unity-ds/api-gateway/integrations/${var.prefix}-uds_api_1-function-name"
  type  = "String"
  value = aws_lambda_function.uds_api_1.function_name
  tags = var.tags
}


resource "aws_ssm_parameter" "health_check_value" {
  count = var.is_deploying_healthcheck ? 1 : 0
  name  = "${var.health_check_base_path}/${var.health_check_marketplace_item}/component/${var.health_check_component_name}"
  type  = "String"
  tier = "Advanced"
  value = jsonencode({
    healthCheckUrl    = "${var.uds_base_url}/${var.dapa_api_prefix}/collections",
    landingPageUrl    = "${var.unity_ui_base_url}/data/stac_browser/",
    componentCategory = "catalogs"
    componentName     = "Data Catalog",
    componentType     = "ui"
    description       = "The STAC Browser to help you browse and search the data catalog for your outputs and other data ingested into the MDPS data system."
  })
  tags = var.tags
  overwrite = true
}

resource "aws_ssm_parameter" "marketplace_prefix" {
  count = var.is_deploying_healthcheck ? 1 : 0
  name  = "/unity/${var.health_check_marketplace_item}/${var.health_check_component_name}/deployment/prefix"
  type  = "String"
  value = var.prefix
  tier = "Advanced"
  tags = var.tags
  overwrite = true
}
