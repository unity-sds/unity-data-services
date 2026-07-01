How to get `smce_deployment` Role

1. Clear content of `~/.aws/credentials` and `~/.aws/config` files
1. Get AWS creds from science cloud:
2. Manually add them to saml-pub

            In Config:
           [profile saml-pub]
           output = json
           region = us-west-2
           sso_session = saml-pub
           sso_account_id = 979188186972
           sso_role_name = Project-Power-User
           [sso-session saml-pub]
           sso_start_url = https://d-9067c5bbc5.awsapps.com/start/#
           sso_region = us-east-1
           sso_registration_scopes = sso:account:access

            In Credentials:
           [saml-pub]
           output = json
           region = us-west-2
           aws_access_key_id=add
           aws_secret_access_key=add
           aws_session_token=add

3. Run the script `smce_keys_assume_deployment.sh`
    - Make sure `TARGET_PROFILE_NAME="mdps-temp-creds-assumed"` not other name
4. Rename that profile to `[default]` in both `~/.aws/credentials` and `~/.aws/config`
