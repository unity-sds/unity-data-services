locals {
  bucket_tags = merge(
    var.tags,
    {
      "Proj" = var.project
      "Venue" = var.venue
      "Env" = var.venue
      "ServiceArea" = "ds"
      "CapVersion" = "1.0.0"
      "Component" = "DatastoreBucket"
      "CreatedBy" = "ds"
      "Stack" = "DatastoreBucket"
      "Capability" = "datastore"
      "Name" = "${var.project}-${var.venue}-ds-datastore-bucket"
    }
  )
}

data "aws_ssm_parameter" "uds_aws_account" {
  name = var.uds_aws_account_ssm_path
}

data "aws_ssm_parameter" "uds_aws_account_region" {
  name = var.uds_aws_account_region_ssm_path
}

data "aws_ssm_parameter" "uds_prefix" {
  name = "arn:aws:ssm:${data.aws_ssm_parameter.uds_aws_account_region.value}:${data.aws_ssm_parameter.uds_aws_account.value}:parameter${var.uds_prefix_ssm_path}"
}
resource "aws_s3_bucket" "datastore_bucket" {
  bucket = lower(replace("${var.project}-${var.venue}-unity-${var.datastore_bucket_name}", "_", "-"))
  tags = local.bucket_tags
}

resource "aws_s3_bucket_server_side_encryption_configuration" "datastore_bucket" {  // https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_server_side_encryption_configuration
  bucket = aws_s3_bucket.datastore_bucket.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "AES256"
    }
  }
}

resource "aws_s3_bucket_policy" "datastore_bucket" {
  // https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_policy
  bucket = aws_s3_bucket.datastore_bucket.id
  policy = templatefile("${path.module}/s3_bucket_policy.json", {
    udsAwsAccount: data.aws_ssm_parameter.uds_aws_account.value,
    s3BucketName: aws_s3_bucket.datastore_bucket.id,
    cumulus_lambda_processing_role_name: "${data.aws_ssm_parameter.uds_prefix.value}-${var.cumulus_lambda_processing_role_name_postfix}",
    cumulus_sf_lambda_role_name: "${data.aws_ssm_parameter.uds_prefix.value}${var.cumulus_sf_lambda_role_name_postfix}",
  })
}

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.datastore_bucket.id
  topic {
    topic_arn     = "arn:aws:sns:${data.aws_ssm_parameter.uds_aws_account_region.value}:${data.aws_ssm_parameter.uds_aws_account.value}:${data.aws_ssm_parameter.uds_prefix.value}-granules_cnm_ingester"
    events        = ["s3:ObjectCreated:*"]
    filter_suffix = ".json"
    filter_prefix = var.datastore_bucket_notification_prefix
  }
}

resource "aws_ssm_parameter" "datastore_bucket" {
  name  = "/unity/${var.project}/${var.venue}/ds/datastore-bucket"
  type  = "String"
  value = aws_s3_bucket.datastore_bucket.bucket
  tags = local.bucket_tags
}