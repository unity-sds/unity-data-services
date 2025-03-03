output "ds_upstream_image" {
  value = "${aws_ecr_pull_through_cache_rule.ds_upstream_image.registry_id}.dkr.ecr.${var.aws_region}.amazonaws.com/${aws_ecr_pull_through_cache_rule.ds_upstream_image.id}/${var.uds_repo_name}:{ImageTag}"
}