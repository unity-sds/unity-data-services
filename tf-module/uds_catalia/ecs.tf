resource "aws_ecs_cluster" "ds_cluster" {
  name = "${var.prefix}-ds_cluster"
}

data "aws_iam_role" "ecs_task_execution_role" {
 #  count = var.create_lambda_role ? 1 : 0
 name = "${var.prefix}-ecs_task_execution_role"
}

resource "aws_cloudwatch_log_group" "ds_cluster" {
  name              = "/ecs/${var.prefix}-ds_cluster"
  retention_in_days = 30
}

resource "aws_ecs_task_definition" "ds_cluster" {
  family                   = "on-demand-task"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = data.aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name      = "app"
      image     = "ghcr.io/my-org/my-image:latest"  # change this
      essential = true
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/${var.prefix}-ds_cluster"
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}



#resource "null_resource" "run_task" {
#  triggers = {
#    always_run = timestamp()
#  }
#
#  provisioner "local-exec" {
#    command = <<EOT
#aws ecs run-task \
#  --cluster ${aws_ecs_cluster.ds_cluster.name} \
#  --launch-type FARGATE \
#  --task-definition ${aws_ecs_task_definition.ds_cluster.arn} \
#  --network-configuration "awsvpcConfiguration={subnets=${jsonencode(var.cumulus_lambda_subnet_ids)},securityGroups=[${data.aws_security_group.uds_lambda_sg_no_ingress_all_egress.id}],assignPublicIp=ENABLED}"
#EOT
#  }
#}
