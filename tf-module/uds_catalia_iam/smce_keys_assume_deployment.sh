#!/bin/bash

# This script fetches initial temporary credentials from an AWS SSO profile,
# then assumes a specified IAM role, and finally exports the assumed role's
# credentials as environment variables. It also configures a separate
# legacy profile with these assumed role credentials.

# --- MANUALLY EDIT THIS SECTION ---
#
# The name of the AWS profile you configured for SSO login.
SSO_PROFILE_NAME="saml-pub"
#
# The name of the new, separate profile that will be created/updated
# with the temporary ASSUMED ROLE credentials.
TARGET_PROFILE_NAME="mdps-temp-creds-assumed" # Renamed for clarity
#
# The AWS Account ID where the target role exists.
# YOU MUST FIND AND ADD THIS 12-DIGIT ID.
TARGET_ACCOUNT_ID="979188186972"
#
# The name of the IAM role you want to assume.
TARGET_ROLE_NAME="smce_deployment"
#
# --- END OF MANUAL EDIT SECTION ---


# --- Script Logic (Do not edit below) ---

# Check if jq is installed, as it's required for parsing JSON.
if ! command -v jq &> /dev/null
then
    echo "❌ Error: 'jq' is not installed. Please install it to proceed."
    echo "In CloudShell, you can install it with: sudo yum install -y jq"
    exit 1
fi

# Validate placeholder Account ID
if [[ "$TARGET_ACCOUNT_ID" == "YOUR_ACCOUNT_ID_HERE" || -z "$TARGET_ACCOUNT_ID" ]]; then
    echo "❌ Error: Please edit the script and replace 'YOUR_ACCOUNT_ID_HERE' with the correct AWS Account ID for the target role."
    exit 1
fi

echo "🔄 Logging in via SSO profile '$SSO_PROFILE_NAME'..."

# First, ensure the user has a valid SSO session by logging in.
# This may open a browser for authentication if your session has expired.
aws sso login --profile "$SSO_PROFILE_NAME"
if [ $? -ne 0 ]; then
    echo "❌ AWS SSO login failed. Please complete the browser authentication and try again."
    exit 1
fi

echo "✅ SSO login successful."
echo "🔄 Fetching initial credentials for SSO profile '$SSO_PROFILE_NAME'..."

# Use the 'export-credentials' command with the 'process' format to get initial temporary credentials as JSON.
initial_credentials_json=$(aws configure export-credentials \
    --profile "$SSO_PROFILE_NAME" \
    --format process)

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to export initial credentials from AWS SSO profile."
    exit 1
fi

# Use jq to parse the initial JSON and extract the credentials.
initial_access_key_id=$(echo "$initial_credentials_json" | jq -r '.AccessKeyId')
initial_secret_access_key=$(echo "$initial_credentials_json" | jq -r '.SecretAccessKey')
initial_session_token=$(echo "$initial_credentials_json" | jq -r '.SessionToken')


echo "what I need to verify exists ${initial_access_key_id}"
# if [ -z "$initial_access_key_id" ] || [ "$initial_access_key_id" == "null" ]; then
#     echo "❌ Error: Could not parse initial credentials from the SSO response."
#     exit 1
# fi

echo "✅ Successfully fetched initial temporary credentials."
echo "🔄 Assuming role '$TARGET_ROLE_NAME' in account '$TARGET_ACCOUNT_ID'..."

# Temporarily set environment variables with the INITIAL credentials
# so the assume-role command can authenticate.
export AWS_ACCESS_KEY_ID="$initial_access_key_id"
export AWS_SECRET_ACCESS_KEY="$initial_secret_access_key"
export AWS_SESSION_TOKEN="$initial_session_token"

# Construct the Role ARN
role_arn="arn:aws:iam::${TARGET_ACCOUNT_ID}:role/${TARGET_ROLE_NAME}"
# Create a unique session name including the username and date
session_name="${USER:-$(whoami)}-$(date +%Y%m%d%H%M%S)"

# Call assume-role using the initial credentials
assumed_role_json=$(aws sts assume-role \
    --role-arn "$role_arn" \
    --role-session-name "$session_name" \
    --output json)

# Unset the temporary initial credentials immediately for security
unset AWS_ACCESS_KEY_ID
unset AWS_SECRET_ACCESS_KEY
unset AWS_SESSION_TOKEN

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to assume role '$TARGET_ROLE_NAME'."
    exit 1
fi

# Parse the credentials for the ASSUMED role
access_key_id=$(echo "$assumed_role_json" | jq -r '.Credentials.AccessKeyId')
secret_access_key=$(echo "$assumed_role_json" | jq -r '.Credentials.SecretAccessKey')
session_token=$(echo "$assumed_role_json" | jq -r '.Credentials.SessionToken')

echo "✅ Successfully assumed role '$TARGET_ROLE_NAME'."
echo ""
echo "--- Configuring profile: '$TARGET_PROFILE_NAME' with ASSUMED role credentials ---"

# Configure the new/target profile with the ASSUMED ROLE temporary credentials.
aws configure set aws_access_key_id "$access_key_id" --profile "$TARGET_PROFILE_NAME"
aws configure set aws_secret_access_key "$secret_access_key" --profile "$TARGET_PROFILE_NAME"
aws configure set aws_session_token "$session_token" --profile "$TARGET_PROFILE_NAME"
aws configure set region "us-west-2" --profile "$TARGET_PROFILE_NAME"

echo "✅ Profile '$TARGET_PROFILE_NAME' has been configured with assumed role keys."
echo ""
echo "--- Exporting ASSUMED role environment variables ---"
echo "To set these for your current session, run this script with 'eval':"
echo "eval \$(./get_sso_keys.sh)"
echo ""

# Print the export commands for the parent shell to evaluate.
# Ensure these use the FINAL assumed role credentials.
export AWS_ACCESS_KEY_ID=$access_key_id
export AWS_SECRET_ACCESS_KEY=$secret_access_key
export AWS_SESSION_TOKEN=$session_token
export AWS_REGION=us-west-2
export AWS_DEFAULT_REGION=us-west-2

echo ""
echo "🚀 Environment variables are ready to be exported for the assumed role '$TARGET_ROLE_NAME'."

