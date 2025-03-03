variable "prefix" {
  type = string
}

variable "ecr_github_username" {
  type = string
  description = "Github username for ECR Pull Through"

}
variable "ecr_github_token" {
  type = string
  description = "Github Fine-grained personal access token for ECR Pull Through that has access to https://github.com/unity-sds/unity-data-services"
}

variable "uds_repo_name" {
  type = string
  default = "unity-sds/unity-data-services"
  description = "Github group and repo"
}