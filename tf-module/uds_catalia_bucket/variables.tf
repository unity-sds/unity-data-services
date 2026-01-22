variable "installprefix" {
  type = string
  default = ""
  description = "This is not needed, but required by UCS Marketplace. Empty string is good enough for manual deployment"
}
variable "deployment_name" {
  type = string
  default = ""
  description = "This is not needed, but required by UCS Marketplace. Empty string is good enough for manual deployment"
}
variable "project" {
  type = string
  default = "UnknownProject"
  description = "Name of Project"
}
variable "venue" {
  type = string
  default = "Unknownvenue"
  description = "Name of Project"
}
variable "tags" {
  description = "Tags to be applied to Cumulus resources that support tags"
  type        = map(string)
  default     = {}
}
variable "account_id" {
  type = string
  description = "AWS Account ID"
}

variable "aws_region" {
  type    = string
  default = "us-west-2"
}

variable "prefix" {
  type = string
}
variable "datastore_bucket_name" {
  type = string
  description = "name of S3 bucket. Note-1: it will be prefixed with '<project prefix>-<project venue>-unity-'. Note-2: It should only have '-'. '_' will be replaced with '-'"
}
variable "datastore_bucket_notification_prefix" {
  type = string
  default = "stage_out"
  description = "path to the directory where catalogs.json will be written"
}

variable "cumulus_lambda_processing_role_name_postfix" {
  type = string
  default = "lambda-processing"
  description = "name of the Lambda Processing role by Cumulus after `prefix`"
}

variable "cumulus_sf_lambda_role_name_postfix" {
  type = string
  default = "_sf_event_sqs_to_db_records_lambda_role"
  description = "name of the Lambda role by Cumulus SF after `prefix`"
}

