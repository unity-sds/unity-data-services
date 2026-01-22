resource "aws_sqs_queue" "dlq" {  // https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sqs_queue
  // TODO how to notify admin for failed ingestion?
  tags = var.tags
  name                      = "${var.prefix}-dlq-${var.name}"
  delay_seconds             = 0
  max_message_size          = 262144
  message_retention_seconds = 345600
  visibility_timeout_seconds = 300
  receive_wait_time_seconds = 0
  policy = templatefile("${path.module}/sqs_policy.json", {
    region: var.aws_region,
    roleArn: var.lambda_processing_role_arn,
    accountId: var.account_id,
    sqsName: "${var.prefix}-dlq-${var.name}",
  })
//  redrive_policy = jsonencode({
//    deadLetterTargetArn = aws_sqs_queue.terraform_queue_deadletter.arn
//    maxReceiveCount     = 4
//  })
//  tags = {
//    Environment = "production"
//  }
}

resource "aws_sqs_queue" "main_sqs" {  // https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sqs_queue
  name                      = "${var.prefix}-${var.name}"
  delay_seconds             = 0
  max_message_size          = 262144
  message_retention_seconds = 345600
  visibility_timeout_seconds = var.cool_off  // Used as cool off time in seconds. It will wait for 5 min if it fails
  receive_wait_time_seconds = 0
  policy = templatefile("${path.module}/sqs_policy.json", {
    region: var.aws_region,
    roleArn: var.lambda_processing_role_arn,
    accountId: var.account_id,
    sqsName: "${var.prefix}-${var.name}",
  })
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = var.retried_count  // How many times it will be retried.
  })
  tags = var.tags
}

resource "aws_sns_topic_subscription" "granules_cnm_ingester_topic_subscription" { // https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sns_topic_subscription
  topic_arn = var.sns_arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.main_sqs.arn
#  filter_policy_scope = "MessageBody"  // MessageAttributes. not using attributes
#  filter_policy = templatefile("${path.module}/ideas_api_job_results_filter_policy.json", {})
}

resource "aws_lambda_event_source_mapping" "granules_cnm_ingester_queue_lambda_trigger" {  // https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_event_source_mapping#sqs
  event_source_arn = aws_sqs_queue.main_sqs.arn
  function_name    = var.lambda_arn
  batch_size = var.sqs_batch_size
  enabled = true
}