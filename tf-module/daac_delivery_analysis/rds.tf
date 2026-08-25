# Create an Autora V2 database and output the url / port / username.
# create a parameter store, secret text mode, and store the url / port / username / password so that applications can pull it to connect them.

terraform {
  required_providers {
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

variable "rds_master_username" {
  type        = string
  default     = "uds_ctla_admin"
  description = "Master username for the Aurora Serverless v2 cluster"
}

variable "rds_database_name" {
  type        = string
  default     = "daac_delivery_analysis"
  description = "Initial database name created in the Aurora Serverless v2 cluster"
}

variable "rds_engine_version" {
  type        = string
  description = "Aurora PostgreSQL engine version. Must be a version that supports Serverless v2 (e.g. \"16.4\")"
  default = "17.9"
}

variable "rds_min_acu" {
  type        = number
  default     = 0.5
  description = "Minimum Aurora Capacity Units (ACUs) for Serverless v2 scaling"
}

variable "rds_max_acu" {
  type        = number
  default     = 1
  description = "Maximum Aurora Capacity Units (ACUs) for Serverless v2 scaling"
}

variable "rds_instance_count" {
  type        = number
  default     = 1
  description = "Number of Aurora Serverless v2 instances to create in the cluster"
}

variable "rds_skip_final_snapshot" {
  type        = bool
  default     = true
  description = "Whether to skip taking a final DB snapshot when the cluster is destroyed"
}

variable "rds_deletion_protection" {
  type        = bool
  default     = false
  description = "Whether to enable deletion protection on the Aurora cluster"
}

resource "random_password" "aurora_master" {
  length           = 32
  special          = true
  override_special = "!#$%^&*()-_=+[]{}<>:?"
}

resource "aws_db_subnet_group" "daac_delivery_analysis" {
  name       = "${var.prefix}-daac-delivery-analysis"
  subnet_ids = var.cumulus_lambda_subnet_ids
  tags       = var.tags
}

resource "aws_security_group" "daac_delivery_analysis_rds" {
  name   = "${var.prefix}-daac-delivery-analysis-rds"
  vpc_id = var.cumulus_lambda_vpc_id
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = local.security_group_ids_set ? var.security_group_ids : [data.aws_security_group.uds_lambda_sg_no_ingress_all_egress.id]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = var.tags
}

resource "aws_rds_cluster" "daac_delivery_analysis" {
  cluster_identifier = "${var.prefix}-daac-delivery-analysis"
  engine             = "aurora-postgresql"
  engine_mode        = "provisioned"
  engine_version     = var.rds_engine_version

  database_name   = var.rds_database_name
  master_username = var.rds_master_username
  master_password = random_password.aurora_master.result

  db_subnet_group_name   = aws_db_subnet_group.daac_delivery_analysis.name
  vpc_security_group_ids = [aws_security_group.daac_delivery_analysis_rds.id]

  storage_encrypted = true

  skip_final_snapshot       = var.rds_skip_final_snapshot
  final_snapshot_identifier = "${var.prefix}-daac-delivery-analysis-final"
  deletion_protection       = var.rds_deletion_protection

  serverlessv2_scaling_configuration {
    min_capacity = var.rds_min_acu
    max_capacity = var.rds_max_acu
  }

  lifecycle {
    ignore_changes = [master_password]
  }

  tags = var.tags
}

resource "aws_rds_cluster_instance" "daac_delivery_analysis" {
  count              = var.rds_instance_count
  cluster_identifier = aws_rds_cluster.daac_delivery_analysis.id
  instance_class     = "db.serverless"
  engine             = aws_rds_cluster.daac_delivery_analysis.engine
  engine_version     = aws_rds_cluster.daac_delivery_analysis.engine_version
  tags               = var.tags
}

resource "aws_ssm_parameter" "daac_delivery_analysis_db_credentials" {
  name = "/${var.prefix}/daac-delivery-analysis/rds_credentials"
  type = "SecureString"
  value = jsonencode({
    URL      = aws_rds_cluster.daac_delivery_analysis.endpoint
    PORT     = aws_rds_cluster.daac_delivery_analysis.port
    USERNAME = var.rds_master_username
    PASSWORD = random_password.aurora_master.result
    DBNAME   = var.rds_database_name
  })
  description = "Secure connection credentials for the DAAC delivery analysis Aurora Serverless v2 database"
  tags        = var.tags
}

output "daac_delivery_analysis_db_url" {
  value = aws_rds_cluster.daac_delivery_analysis.endpoint
}

output "daac_delivery_analysis_db_port" {
  value = aws_rds_cluster.daac_delivery_analysis.port
}

output "daac_delivery_analysis_db_username" {
  value = var.rds_master_username
}
