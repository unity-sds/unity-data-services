resource "aws_api_gateway_method" "uds_all_options_method" {
    rest_api_id   = var.rest_api_id
    resource_id   = var.resource_id
    operation_name = "${var.prefix}-uds_cors"
    http_method   = "OPTIONS"
    authorization = "NONE"
}
resource "aws_api_gateway_method_response" "uds_all_options_200" {
    rest_api_id   = var.rest_api_id
    resource_id   = var.resource_id
    http_method   = aws_api_gateway_method.uds_all_options_method.http_method
    status_code   = 200
    response_models = {
        "application/json" = "Empty"
    }
    response_parameters = var.cors_200_response_parameters
    depends_on = ["aws_api_gateway_method.uds_all_options_method"]
}
resource "aws_api_gateway_integration" "uds_all_options_integration" {
    rest_api_id   = var.rest_api_id
    resource_id   = var.resource_id
    http_method   = aws_api_gateway_method.uds_all_options_method.http_method
        type          = "MOCK"
    request_templates = {
      "application/json" = jsonencode(
        {
          statusCode = 200
        })
    }
    depends_on = ["aws_api_gateway_method.uds_all_options_method"]
}

resource "aws_api_gateway_integration_response" "uds_all_options_integration_response" {
    rest_api_id   = var.rest_api_id
    resource_id   = var.resource_id
    http_method   = aws_api_gateway_method.uds_all_options_method.http_method
    status_code   = aws_api_gateway_method_response.uds_all_options_200.status_code
    response_parameters = var.cors_integration_response
    depends_on = ["aws_api_gateway_method_response.uds_all_options_200"]
}
output "options_integration_object" {
    value = aws_api_gateway_integration.uds_all_options_integration
}