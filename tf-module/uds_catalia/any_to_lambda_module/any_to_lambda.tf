resource "aws_api_gateway_method" "uds_all_method" {
  rest_api_id        = var.rest_api_id
  resource_id        = var.resource_id
  http_method        = "ANY"
  authorization      = "CUSTOM"
  authorizer_id      = var.authorizer_id
  request_parameters = {
    "method.request.path.proxy" = true
  }
}

resource "aws_api_gateway_method_response" "uds_all_method_response" {
  rest_api_id     = var.rest_api_id
  resource_id     = var.resource_id
  http_method     = aws_api_gateway_method.uds_all_method.http_method
  status_code     = 200
  response_models = {
    "application/json" = "Empty"
  }
  #    response_parameters = {
  #        "method.response.header.Access-Control-Allow-Origin" = true
  #    }
  depends_on = ["aws_api_gateway_method.uds_all_method"]
}

resource "aws_api_gateway_integration" "uds_all_lambda_integration" {
  rest_api_id             = var.rest_api_id
  resource_id             = var.resource_id
  http_method             = aws_api_gateway_method.uds_all_method.http_method
  type                    = "AWS_PROXY"
  uri                     = var.lambda_invoke_arn
  integration_http_method = "POST"

  #  cache_key_parameters = ["method.request.path.proxy"]

  timeout_milliseconds = 29000
  #  request_parameters = {
  #    "integration.request.path.proxy" = "method.request.path.proxy"
  #  }
}

output "lambda_integration_object" {
    value = aws_api_gateway_integration.uds_all_lambda_integration
}