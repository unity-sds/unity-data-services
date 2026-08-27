## Steps to run terraform modules to deploy Catalia UDS Resources

### Preparing AWS credentials
1. This terraform is setup to run in Science Cloud http://aws.sciencecloud.nasa.gov/ There may be some changes needed for other cloud. 
2. Retrieve Access Keys for `Project-Power-User`, and set it as `saml-pub-smce`

```
~/.aws/credentials
[saml-pub-smce]
aws_access_key_id = xxx
aws_secret_access_key = xxx
aws_session_token = xxx

~/.aws/config
[profile saml-pub-smce]
output = json
region = us-west-2
sso_session = saml-pub-smce
sso_account_id = <account-id>
sso_role_name = Project-Power-User
```
3. Get elevated credential via /tf-module/uds_catalia/smce_keys_assume_deployment.sh. It is looking for `saml-pub-smce` profile, and output is in `mdps-temp-creds-assumed`. 
4. Check ~/.aws/credentials and ~/.aws/config files and verify `mdps-temp-creds-assumed` is created and values are valid. 
5. export the above profile as default. 

### Setting up VPC. 
1. VPC should be setup by SA or a project admin. 
2. If missing, there is a unity VPC terraform which can be used to setup a VPC. `/tf-module/unity_vpc`

### Setting up IAM
1. Using VPC above, `/tf-module/uds_catalia_iam` sets up most of IAM roles needed for lambdas, and others. 
2. *NOTE*: In Variables, there is a `prefix`. The `prefix` value must match between this module and the following modules such has `/tf-module/uds_catalia`
### Setting up Bucket (Optional)
1. This is a legacy bucket where initial workflow requires data to be staged in UDS bucket. 
2. If needed, `/tf-module/uds_catalia_bucket` can be used to setup a bucket. 

### Deploying Aurora V2 (Optional)
1. This should be replaced with Postgres DB from MAAP. 
2. IF needed, `/tf-module/daac_delivery_analysis` can be used to deploy a minimal Aurora DB. 
3. It will create a parameter store with the following JSON `{\"DBNAME\":\"xxx\",\"PASSWORD\":\"xxx\",\"PORT\":xxx,\"URL\":\"xxx\",\"USERNAME\":\"xxx\"}`

### Manually creating Postgres Connection String in Parameter Store
1. If Aurora V2 is not created, there needs to be a parameter store with the following JSON `{\"DBNAME\":\"xxx\",\"PASSWORD\":\"xxx\",\"PORT\":xxx,\"URL\":\"xxx\",\"USERNAME\":\"xxx\"}`
``
### Setting up Catalia DAAC Delivery
1. Deploy main resources `/tf-module/uds_catalia` which includes Lambda, API Gateway, SNS/SQS pipeline. 
2. Lambda zip file needs to be downloaded from https://github.com/unity-sds/unity-data-services/releases where each release has a `cumulus_lambda_functions-<version>-*.zip` file. It is re-used for all lambda functions.
3. The zip file must be renamed and placed at the `/tf-module/uds_catalia/build/cumulus_lambda_functions_deployment.zip`
3. `CATALYA_RDS_CREDS_PARAM_PATH` is retrieved from `Deploying Aurora V2 (Optional)` or `Manually creating Postgres Connection String in Parameter Store`
4. `DAAC_LAMBDA_2_SNS_ROLE` needs to be DAAC role. If unknown, put dummy value at this moment, and update it when needed. 


