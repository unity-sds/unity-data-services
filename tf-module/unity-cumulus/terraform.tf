terraform {
  backend "s3" {
    region         = "us-west-2"
    bucket         = "am-uds-dev-cumulus-tf-state"
    key            = "am-uds-dev-cumulus/cumulus/unity/terraform.tfstate"
    dynamodb_table = "am-uds-dev-cumulus-tf-locks"
  }
}
