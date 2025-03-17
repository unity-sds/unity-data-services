resource "aws_iam_role" "ds_stac_browser_profile_role" {
  name = "${var.prefix}-ds_stac_browser_profile_role"
  permissions_boundary = "arn:aws:iam::${local.account_id}:policy/mcp-tenantOperator-AMI-APIG"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "ec2.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}


resource "aws_iam_role_policy_attachment" "ds_stac_browser_profile_role_policy_attachment_ssm" {
  role       = aws_iam_role.ds_stac_browser_profile_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role_policy_attachment" "ds_stac_browser_profile_role_policy_attachment_cloudwatch" {
  role       = aws_iam_role.ds_stac_browser_profile_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

resource "aws_iam_instance_profile" "ds_stac_browser_profile" {
  name = "${var.prefix}-ds_stac_browser_profile"
  role = aws_iam_role.ds_stac_browser_profile_role.name
}



resource "aws_security_group" "ds_stac_browser_security_group" {
  name = "${var.prefix}-ds_stac_browser_security_group"
  description = "Allow TLS inbound traffic and all outbound traffic"
  vpc_id      = var.cumulus_lambda_vpc_id
  tags = var.tags
}

resource "aws_vpc_security_group_ingress_rule" "ds_stac_browser_security_group_443_10" {
  security_group_id = aws_security_group.ds_stac_browser_security_group.id
  cidr_ipv4         = var.alb_subnet_cidr
  from_port         = 8005
  ip_protocol       = "tcp"
  to_port           = 8005
}

resource "aws_vpc_security_group_egress_rule" "ds_stac_browser_security_group_outb_ipv4" {
  security_group_id = aws_security_group.ds_stac_browser_security_group.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1" # semantically equivalent to all ports
}

resource "aws_vpc_security_group_egress_rule" "ds_stac_browser_security_group_outb_ipv6" {
  security_group_id = aws_security_group.ds_stac_browser_security_group.id
  cidr_ipv6         = "::/0"
  ip_protocol       = "-1" # semantically equivalent to all ports
}

resource "aws_instance" "ds_stac_browser" {
  subnet_id     = var.subnet_ids[0]
  security_groups = [aws_security_group.ds_stac_browser_security_group.id]
  ami                    = var.ami_id
  instance_type          = var.instance_type
  associate_public_ip_address = false
  iam_instance_profile   = aws_iam_instance_profile.ds_stac_browser_profile.name
  user_data = templatefile("${path.module}/ec2_start.txt", {
    github_image_url: var.github_image_url,
    image_tag: var.image_tag,
  })
  tags = {
    Name = "${var.prefix}-ds_stac_browser"
  }
}
