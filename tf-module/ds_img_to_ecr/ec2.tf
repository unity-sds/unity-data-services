data "aws_iam_instance_profile" "ec2_profile" {
  name = var.ec2_profile_iam_name
}
data "aws_subnet" "ec2_subnet" {
  id = var.cumulus_subnet_id
}

resource "aws_instance" "docker_builder" {
  subnet_id     = data.aws_subnet.ec2_subnet.id
  security_groups = var.security_group_id
  ami                    = var.ami_id
  instance_type          = var.instance_type
  key_name               = var.key_name
  associate_public_ip_address = true
  iam_instance_profile   = data.aws_iam_instance_profile.ec2_profile.name

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
    Name = "Docker-Build-Instance"
  }
}

