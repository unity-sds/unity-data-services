#data "aws_sns_topic" "report_granules_topic" {  // https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sns_topic.html
#  name              = var.report_granules_topic
#}

module "granules_to_es" {
  source = "./sqs--sns-lambda-connector"

  account_id                 = local.account_id
  lambda_arn                 = aws_lambda_function.granules_to_es.arn
  lambda_processing_role_arn = var.lambda_processing_role_arn
  name                       = "granules_to_es"
  prefix                     = var.prefix
#  sns_arn                    = data.aws_sns_topic.report_granules_topic.arn
  sns_arn                    = var.report_granules_topic
}
