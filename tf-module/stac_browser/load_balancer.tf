resource "aws_security_group" "ds_alb_security_group" {
  name = "${var.prefix}-ds_alb_security_group"
  description = "Allow TLS inbound traffic and all outbound traffic"
  vpc_id      = var.cumulus_lambda_vpc_id
  tags = var.tags
}

resource "aws_vpc_security_group_ingress_rule" "ds_alb_security_group_443_10" {
  security_group_id = aws_security_group.ds_alb_security_group.id
  cidr_ipv4         = var.shared_services_ec2_subnet_cidr
  from_port         = 8005
  ip_protocol       = "tcp"
  to_port           = 8005
}

resource "aws_vpc_security_group_egress_rule" "ds_alb_security_group_outb_ipv4" {
  security_group_id = aws_security_group.ds_alb_security_group.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1" # semantically equivalent to all ports
}

resource "aws_vpc_security_group_egress_rule" "ds_alb_security_group_outb_ipv6" {
  security_group_id = aws_security_group.ds_alb_security_group.id
  cidr_ipv6         = "::/0"
  ip_protocol       = "-1" # semantically equivalent to all ports
}

resource "aws_lb" "ds_alb" {
  name = lower(replace("${var.prefix}-ds_alb", "_", "-"))
  internal           = true  # To be confirmed
  load_balancer_type = "application"
  security_groups    = [aws_security_group.ds_alb_security_group.id]
  subnets            = var.subnet_ids

  enable_deletion_protection = true

#  access_logs {
#    bucket  = aws_s3_bucket.lb_logs.id
#    prefix  = "test-lb"
#    enabled = true
#  }

  tags = var.tags
}

resource "aws_lb_listener" "ds_stac_browser" {
  load_balancer_arn = aws_lb.ds_alb.arn
  port              = "8005"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ds_stac_browser.arn
  }
}

resource "aws_lb_target_group" "ds_stac_browser" {
  name = lower(replace("${var.prefix}-ds_stac_browser", "_", "-"))
  target_type = "instance"
  port        = 8005
  protocol    = "HTTP"
  vpc_id      = var.cumulus_lambda_vpc_id

  health_check {
    path                = "/"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
}

resource "aws_lb_target_group_attachment" "app_attachment" {
  target_group_arn = aws_lb_target_group.ds_stac_browser.arn
  target_id        = aws_instance.ds_stac_browser.id
  port             = 8005
}
