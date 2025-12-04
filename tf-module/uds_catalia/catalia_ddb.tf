resource "aws_dynamodb_table" "uds_ctla_auth_ddb" {
  name         = "${var.prefix}-uds_ctla_auth_ddb"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "userGroup"
  range_key    = "projectMap"

  attribute {
    name = "userGroup"
    type = "S"
  }

  attribute {
    name = "projectMap"
    type = "S"
  }
#  attribute {
#    name = "access"
#    type = "B"
#  }

  global_secondary_index {
    name               = "${var.prefix}-uds_ctla_auth_ddb_gsi_user_group"
    hash_key           = "userGroup"
    projection_type    = "KEYS_ONLY"
  }
#
#  global_secondary_index {
#    name            = "GSI2_Project_Venue"
#    hash_key        = "Project"
#    range_key       = "Venue"
#    projection_type = "KEYS_ONLY"
#  }
}

resource "aws_dynamodb_table" "uds_ctla_daac_handshake" {
  name         = "${var.prefix}-uds_ctla_daac_handshake"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "sourceProject"
  range_key    = "targetProject"

  attribute {
    name = "sourceProject"
    type = "S"
  }

  attribute {
    name = "targetProject"
    type = "S"
  }

#  global_secondary_index {
#    name               = "${var.prefix}-uds_auth_ddb_gsi_"
#    hash_key           = "userGroup"
#    projection_type    = "KEYS_ONLY"
#  }
#
#  global_secondary_index {
#    name            = "GSI2_Project_Venue"
#    hash_key        = "Project"
#    range_key       = "Venue"
#    projection_type = "KEYS_ONLY"
#  }
}