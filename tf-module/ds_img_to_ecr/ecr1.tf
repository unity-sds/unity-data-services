provider "aws" {
  region = var.aws_region

  ignore_tags {
    key_prefixes = ["gsfc-ngap"]
  }
}
data "aws_caller_identity" "current" {}

locals {
  account_id = data.aws_caller_identity.current.account_id
}


resource "aws_ecr_repository" "repo" {
  name = var.ecr_repo_name
  image_tag_mutability = "IMMUTABLE"
  encryption_configuration {
    encryption_type = "AES256"
  }
}

output "ecr_repo_url" {
  value = aws_ecr_repository.repo.repository_url
}

resource "null_resource" "docker_pull_push" {
  provisioner "local-exec" {
    command = <<EOT
      aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${aws_ecr_repository.repo.repository_url}
      docker pull  --platform=linux/amd64 ${var.github_image_url}:${var.image_tag}
      docker tag ${var.github_image_url}:${var.image_tag} ${aws_ecr_repository.repo.repository_url}:${var.image_tag}
      docker push ${aws_ecr_repository.repo.repository_url}:${var.image_tag}
    EOT
  }
  depends_on = [aws_ecr_repository.repo]
}