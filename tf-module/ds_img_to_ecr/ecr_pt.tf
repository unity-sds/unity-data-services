resource "random_string" "suffix" {
  length  = 6
  special = false
}

# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret
resource "aws_secretsmanager_secret" "ds_upstream_image" {
  name = replace("ecr-pullthroughcache/${var.prefix}-ds_upstream_image-${random_string.suffix.result}", "_", "-")
}

# https://registry.terraform.io/providers/-/aws/latest/docs/resources/ecr_pull_through_cache_rule
resource "aws_ecr_pull_through_cache_rule" "ds_upstream_image" {
  ecr_repository_prefix = "mdps-github"
  upstream_registry_url = "ghcr.io"
  credential_arn        = aws_secretsmanager_secret.ds_upstream_image.arn
}

# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret_version
resource "aws_secretsmanager_secret_version" "ds_upstream_image" {
  secret_id     = aws_secretsmanager_secret.ds_upstream_image.id
  secret_string = jsonencode({
    username    = var.ecr_github_username
    accessToken = var.ecr_github_token
  })
}