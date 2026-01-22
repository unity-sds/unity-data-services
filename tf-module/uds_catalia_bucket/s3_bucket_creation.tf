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
    udsAwsAccount: var.account_id,
    s3BucketName: aws_s3_bucket.datastore_bucket.id,
    cumulus_lambda_processing_role_name: "${var.prefix}-lambda-processing",
  })
}
