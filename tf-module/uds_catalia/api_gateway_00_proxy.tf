resource "aws_api_gateway_resource" "uds_all_resource" {
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  parent_id   = aws_api_gateway_resource.uds_api_base_resource.id
  path_part   = "{proxy+}"
}

module "uds_all_any_to_lambda_module" {
  source = "./any_to_lambda_module"
  authorizer_id = aws_api_gateway_authorizer.unity_cognito_authorizer.id
  lambda_invoke_arn = aws_lambda_function.uds_api_1.invoke_arn
  rest_api_id      = aws_api_gateway_rest_api.rest_api.id
  resource_id      = aws_api_gateway_resource.uds_all_resource.id
}

module "uds_all_cors_method" {
  source           = "./cors_module"
  rest_api_id      = aws_api_gateway_rest_api.rest_api.id
  resource_id      = aws_api_gateway_resource.uds_all_resource.id
  prefix           = "${var.prefix}_uds_all"
}