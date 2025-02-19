variable "aws_region" {
  type    = string
  default = "us-west-2"
}
variable "tags" {
  description = "Tags to be applied to Cumulus resources that support tags"
  type        = map(string)
  default     = {}
}

variable "github_image_url" {
  description = "The full URL of the public Docker image on GitHub (e.g., ghcr.io/user/repo)"
  default = "ghcr.io/unity-sds/unity-data-services"
  type        = string
}

variable "image_tag" {
  description = "The tag of the image to pull from GitHub"
  type        = string
}

variable "ecr_repo_name" {
  description = "The name of the ECR repository"
  default = "unity-data-services"
  type        = string
}