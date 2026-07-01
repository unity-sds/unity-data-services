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

variable "rest_api_id" {
  type = string
}

variable "resource_id" {
  type = string
}

variable "prefix" {
  type = string
}
