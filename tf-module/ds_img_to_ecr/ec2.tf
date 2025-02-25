resource "aws_iam_role" "ec2_docker_builder_profile_role" {
  name = "${var.prefix}-ec2_docker_builder_profile_role"
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


# IAM Policy for accessing S3 and SNS in other accounts
resource "aws_iam_policy" "ec2_docker_builder_profile_role_policy" {
  name        = "${var.prefix}-ec2_docker_builder_profile_role_policy"
  description = ""
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:GetAuthorizationToken",
          "ecr:BatchGetImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:PutImage",
          "ec2:TerminateInstances"
        ],
        "Resource": "*"
      },

    ]
  })
}

# Attach policy to the role
resource "aws_iam_role_policy_attachment" "ec2_docker_builder_profile_role_policy_attachment" {
  role       = aws_iam_role.ec2_docker_builder_profile_role.name
  policy_arn = aws_iam_policy.ec2_docker_builder_profile_role_policy.arn
}

resource "aws_iam_role_policy_attachment" "ec2_docker_builder_profile_role_policy_attachment_ssm" {
  role       = aws_iam_role.ec2_docker_builder_profile_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role_policy_attachment" "ec2_docker_builder_profile_role_policy_attachment_cloudwatch" {
  role       = aws_iam_role.ec2_docker_builder_profile_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

resource "aws_iam_instance_profile" "ec2_docker_builder_profile" {
  name = "${var.prefix}-ec2_docker_builder_profile"
  role = aws_iam_role.ec2_docker_builder_profile_role.name
}

data "aws_subnet" "ec2_subnet" {
  id = var.cumulus_subnet_id
}

resource "aws_security_group" "ec2_docker_builder_security_group" {
  name = "${var.prefix}-ec2_docker_builder_security_group"
  description = "Allow TLS inbound traffic and all outbound traffic"
  vpc_id      = var.cumulus_lambda_vpc_id
  tags = var.tags
}

resource "aws_vpc_security_group_ingress_rule" "ec2_docker_builder_security_group_443_128" {
  security_group_id = aws_security_group.ec2_docker_builder_security_group.id
  cidr_ipv4         = "128.149.0.0/16"
  from_port         = 443
  ip_protocol       = "tcp"
  to_port           = 443
}

resource "aws_vpc_security_group_ingress_rule" "ec2_docker_builder_security_group_443_137" {
  security_group_id = aws_security_group.ec2_docker_builder_security_group.id
  cidr_ipv4         = "137.79.0.0/16"
  from_port         = 443
  ip_protocol       = "tcp"
  to_port           = 443
}

resource "aws_vpc_security_group_egress_rule" "ec2_docker_builder_security_group_outb_ipv4" {
  security_group_id = aws_security_group.ec2_docker_builder_security_group.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1" # semantically equivalent to all ports
}

resource "aws_vpc_security_group_egress_rule" "ec2_docker_builder_security_group_outb_ipv6" {
  security_group_id = aws_security_group.ec2_docker_builder_security_group.id
  cidr_ipv6         = "::/0"
  ip_protocol       = "-1" # semantically equivalent to all ports
}

resource "aws_instance" "docker_builder" {
  subnet_id     = data.aws_subnet.ec2_subnet.id
  security_groups = [aws_security_group.ec2_docker_builder_security_group.id]
  ami                    = var.ami_id
  instance_type          = var.instance_type
  associate_public_ip_address = false
  iam_instance_profile   = aws_iam_instance_profile.ec2_docker_builder_profile.name

  user_data = <<-EOF
    #!/bin/bash
    set -e

    # Install Docker
    yum update -y
    amazon-linux-extras enable docker
    yum install -y docker
    service docker start
    usermod -aG docker ec2-user

    # Install AWS CLI (if not already installed)
    yum install -y aws-cli

    # Login to ECR
    aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${aws_ecr_repository.repo.repository_url}

    # Pull the AMD64 image
    docker pull --platform=linux/amd64 ${var.github_image_url}:${var.image_tag}

    # Tag and push the image to ECR
    docker tag ${var.github_image_url}:${var.image_tag} ${aws_ecr_repository.repo.repository_url}:${var.image_tag}
    docker push ${aws_ecr_repository.repo.repository_url}:${var.image_tag}


    TOKEN=`curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600"`
    INSTANCE_ID=`curl http://169.254.169.254/latest/meta-data/instance-id -H "X-aws-ec2-metadata-token: $TOKEN"`
    aws ec2 terminate-instances --instance-ids $INSTANCE_ID --region ${var.aws_region}
  EOF

  tags = {
    Name = "${var.prefix}-docker_builder"
  }
}

