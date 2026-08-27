## Steps to perform after negotiation with DAAC. 

1. Find out the User Group (from MAAP Keycloak) and Algorithm Name and Version responsible for the collection to be sent to the DAAC. 
2. Run 2 Admin calls to add them. Examples:
```
        result = s.post(f'{BASE_URL}/admin/auth', json={
            'source': source_collection,
            'target': target_collection,
            'group_name': 'GEDI PA',
            'access': True,
        })
        
        
        result = s.post(f'{BASE_URL}/admin/auth/algorithm', json={
            'source': source_collection,
            'target': target_collection,
            "algorithm_name": "py-tropess_57",
            "algorithm_version": "1.6.1",
            'access': True,
        })
```
3. Ask for the values of `daac_provider`, `daac_sns_topic_arn`, `daac_role_arn`, `daac_role_session_name` from the DAAC. 
4. Ask for the value of `daac_data_version` from the DAAC. This is their collection version. 
5. Ask for the value of  `api_key` from the DAAC if applicable. 
6. Ask for the `archiving_types` from the source users. 
    - If it's empty, everything will be archived.
    - If `data_type` is present, matching names from STAC's assets' role will be archived. 
    - If `file_extension` list is present, files with same extensions and same `data_type` will be archived. 
7. Run DAAC Handshake config. Example:
```
            result = s.post(f'{BASE_URL}/collections/{source_collection}/{target_collection}/archive', json={
                    "api_key": "FAKE",
                    "daac_provider": "gesdisc_tropess_testing",
                    "daac_data_version": "2",
                    'daac_sns_topic_arn': 'arn:aws:sns:us-west-2:xxx:gesdisc-cumulus-uat-CNM-ingest',
                    'daac_role_arn': 'arn:aws:iam::xxx:role/TROPESS_ingest_deletion',
                    'daac_role_session_name': 'tropess_request',
                    "archiving_types": [{
                    "data_type": "data"
                }],
            })

```
8. In our S3 data Bucket(s), add this to the bucket policy. NOTE that Principal > AWS > role needs to be updated. 
```
        {
            "Sid": "GesdiscS3Access",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::xxx:role/cnsld-cumulus-uat3-lambda-processing",
                "Service": "s3.amazonaws.com"
            },
            "Action": [
                "s3:ListBucket",
                "s3:GetObject*"
            ],
            "Resource": [
                "arn:aws:s3:::maap-uat-workspace",
                "arn:aws:s3:::maap-uat-workspace/*"
            ]
        }
```
9. Pass our `SNS ARN` and `S3 data bucket(s) ARN` to the DAAC so that they can update their IAM roles.  
10. Deploy or update `/tf-module/uds_catalia` where terraform.tfvars is updated for this variable `DAAC_LAMBDA_2_SNS_ROLE`. This will update SNS Access policy to accept messages from DAAC.
```
DAAC_LAMBDA_2_SNS_ROLE="arn:aws:iam::xxx:role/cnsld-cumulus-uat3-lambda-processing"
```