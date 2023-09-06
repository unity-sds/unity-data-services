
permissions_boundary_arn                 = "arn:aws:iam::884500545225:policy/Security_Boundary_NoIAM"
prefix  = "am-uds-dev-cumulus"
cumulus_lambda_subnet_ids    = ["subnet-00cacaab15b901d53", "subnet-068f7d5c0a859d710"]
cumulus_lambda_vpc_id        = "vpc-06e627ef021d1854e"
security_group_ids = ["sg-045f9c24c760940b6"]
aws_region = "us-west-2"
cumulus_base = "https://na/dev"
cnm_sns_topic_arn = "arn:aws:sns:us-west-2:884500545225:am-uds-dev-cumulus-cnm-submission-sns"
lambda_processing_role_arn = "arn:aws:iam::884500545225:role/am-uds-dev-cumulus-lambda-processing"