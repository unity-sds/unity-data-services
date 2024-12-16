variable "log_level" {
  type = string
  default = "20"
  description = "Lambda Log Level. Follow Python3 log level numbers info=20, warning=30, etc..."
}
variable "account_id" {
  type = string
  description = "AWS Account ID"
}
variable "valid_file_type" {
  type = string
  description = "metadata type name which is used to check if a file should be read as JSON metadata file"
  default = "metadata"
}
variable "metadata_stac_file_postfix" {
  type = string
  description = "Comma separated File Postfix for STAC JSON metadata files"
  default = "STAC.JSON"
}
variable "metadata_s4pa_file_postfix" {
  type = string
  description = "Comma separated File Postfix for PDS XML metadata files"
}
variable "prefix" {
  type = string
}
variable "aws_region" {
  type    = string
  default = "us-west-2"
}
variable "cumulus_lambda_subnet_ids" {
  description = "Subnet IDs for Lambdas"
  type        = list(string)
  default     = null
}
variable "cumulus_lambda_vpc_id" {
  type = string
}
variable "permissions_boundary_arn" {
  type    = string
  default = null
}
variable "security_group_ids" {
  description = "Security Group IDs for Lambdas"
  type        = list(string)
  default     = null
}

variable "tags" {
  description = "Tags to be applied to Cumulus resources that support tags"
  type        = map(string)
  default     = {}
}

variable "cnm_sns_topic_arn" {
  description = "SNS ARN of CNM submission topic"
  type = string
}

variable "workflow_sqs_url" {
  type = string
  description = "SNS ARN of CNM submission topic"
}

variable "unity_default_provider" {
  type = string
  description = "default provider name"

}

variable "cors_origins" {
  default = ""
  type = string
  description = "Comma separated origins for CORS"
}

variable "dapa_api_prefix" {
  type = string
  description = "An API Gateway resource to identify the Project Name that this specific resource is integrated with"
  default = "am-uds-dapa"
}

variable "uds_base_url" {
  type = string
}

variable "unity_ui_base_url" {
  type = string
  description = "Example: https://www.dev.mdps.mcp.nasa.gov:4443. Make sure it does NOT end with `/`"
}

variable "report_to_ems" {
  type = string
  default = "TRUE"
}

variable "cumulus_base" {
  type = string
  description = "Cumulus base URL. Example: https://axhmoecy02.execute-api.us-west-2.amazonaws.com/dev"
}

variable "register_custom_metadata" {
  type = string
  default = "TRUE"
  description = "flag to decide if custom metadata will be added. "
}

variable "lambda_processing_role_arn" {
  type = string
}

variable "uds_es_cluster_instance_count" {
  type = number
  default = 2
  description = "How many EC2 instances for Opensearch"
}

variable "uds_es_cluster_instance_type" {
  type = string
  default = "r5.large.elasticsearch"
  description = "EC2 instance type for Opensearch"
}

variable "comma_separated_admin_groups" {
  type = string
  description = "comma separated cognito groups which will be authorized as ADMIN group"
}

variable "report_granules_topic" {
  type = string
  description = "SNS name"
}

variable "shared_services_rest_api_name" {
  type        = string
  description = "Shared services REST API name"
  default     = "Unity Shared Services REST API Gateway"
}

variable "rest_api_stage" {
  type        = string
  description = "REST API Stage Name"
  default     = "dev"
}

variable "unity_cognito_authorizer__authorizer_id" {
  type = string
  description = "Example: 0h9egs"
}

variable "cors_200_response_parameters" {
  type = map(bool)
  default = {
        "method.response.header.Access-Control-Allow-Credentials" = true
        "method.response.header.Access-Control-Allow-Headers" = true
        "method.response.header.Access-Control-Allow-Methods" = true
        "method.response.header.Access-Control-Allow-Origin" = true
        "method.response.header.Access-Control-Expose-Headers" = true
        "method.response.header.Access-Control-Max-Age" = true
    }
}

variable "cors_integration_response" {
  type = map(string)
  default = {
        "method.response.header.Access-Control-Allow-Credentials" = "'true'",
        "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
        "method.response.header.Access-Control-Allow-Methods" = "'DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT'",
        "method.response.header.Access-Control-Allow-Origin" = "'*'"
        "method.response.header.Access-Control-Expose-Headers" = "'Access-Control-Allow-Methods,Access-Control-Expose-Headers,Access-Control-Max-Age'"
        "method.response.header.Access-Control-Max-Age" = "'300'"
    }
}


variable "health_check_marketplace_item" {
  type = string
  default = "shared-services"
  description = "name of the portion of Marketplace item as path of SSM token"
}

variable "health_check_component_name" {
  type = string
  default = "data-catalog"
  description = "name of the portion of Marketplace item as path of SSM token"
}

variable "is_deploying_healthcheck" {
  type = bool
  default = true
  description = "flag to specify if deploying health check"
}

variable "health_check_base_path" {
  type = string
  default = "/unity"
  description = "base path for healthcheck which should start with, but not end with `/`"
}

//         <<  Variables for granules_cnm_ingester   >>
variable "granules_cnm_ingester__sqs_visibility_timeout_seconds" {
  type = number
  default = 300
  description = "when a lambda ends in error, how much sqs should wait till it is retried again. (in seconds). defaulted to 5 min"
}

variable "granules_cnm_ingester__sqs_retried_count" {
  type = number
  default = 3
  description = "How many times it is retried before pushing it to DLQ. defaulted to 3 times"
}

variable "granules_cnm_ingester__lambda_concurrency" {
  type = number
  default = 20
  description = "How many Lambdas can be executed for CNM ingester concurrently"
}

variable "granules_cnm_response_writer__lambda_concurrency" {
  type = number
  default = 20
  description = "How many Lambdas can be executed for CNM Response Writer concurrently"
}

variable "granules_cnm_response_topic" {
  type = string
  description = "Name of CNM Response SNS Topic"
}

variable "granules_cnm_ingester__bucket_notification_prefix" {
  type = string
  default = "stage_out"
  description = "path to the directory where catalogs.json will be written"
}

variable "granules_cnm_ingester__s3_glob" {
    type = string
  default = "*unity*"
  description = "GLOB expression that has all s3 buckets connecting to SNS topic"
}
#variable "granules_cnm_ingester__is_deploying_bucket" {
#  type = bool
#  default = false
#  description = "flag to specify if deploying example bucket"
#}
//         <<  Variables for granules_cnm_ingester END   >>
