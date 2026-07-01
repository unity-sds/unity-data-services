resource "aws_api_gateway_resource" "openapi_resource" {
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  parent_id   = aws_api_gateway_resource.uds_api_base_resource.id
  path_part   = "openapi"
}

resource "aws_api_gateway_method" "openapi_method" {
  rest_api_id   = aws_api_gateway_rest_api.rest_api.id
  resource_id   = aws_api_gateway_resource.openapi_resource.id
  http_method   = "GET"
  authorization = "NONE"
  request_parameters = {
    "method.request.path.proxy" = true
  }
}

resource "aws_api_gateway_integration" "openapi_lambda_integration" {
  rest_api_id   = aws_api_gateway_rest_api.rest_api.id
  resource_id          = aws_api_gateway_resource.openapi_resource.id
  http_method          = aws_api_gateway_method.openapi_method.http_method
  type                 = "AWS_PROXY"
  uri = aws_lambda_function.uds_api_1.invoke_arn
  integration_http_method = "POST"

#  cache_key_parameters = ["method.request.path.proxy"]

  timeout_milliseconds = 29000
#  request_parameters = {
#    "integration.request.path.proxy" = "method.request.path.proxy"
#  }
}

##########################################################################################################################