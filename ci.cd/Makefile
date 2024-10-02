export IMAGE_PREFIX ?= cae-artifactory.jpl.nasa.gov:16001/gov/nasa/jpl/unity
export NAME ?= uds
export VERSION ?= latest


all: build_lambda upload_lambda update_lambda_function build_docker
local: build_lambda upload_lambda
build_docker:
	docker build --no-cache -t "$(IMAGE_PREFIX)/$(NAME):$(VERSION)" -f docker/Dockerfile_download_granules.jpl .

zip_docker:
	docker save "$(IMAGE_PREFIX)/$(NAME):$(VERSION)" | gzip > "$(NAME)__$(VERSION).tar.gz"

build_lambda:
	docker run --rm -v `PWD`:"/usr/src/app/cumulus_lambda_functions":z -w "/usr/src/app/cumulus_lambda_functions" cae-artifactory.jpl.nasa.gov:17001/python:3.9 ci.cd/create_s3_zip.sh

build_lambda_public:
	docker run --rm -v `PWD`:"/usr/src/app/cumulus_lambda_functions":z -w "/usr/src/app/cumulus_lambda_functions" python:3.9 ci.cd/create_s3_zip.sh

upload_lambda:
	aws --profile saml-pub s3 cp cumulus_lambda_functions_deployment.zip s3://am-uds-dev-cumulus-tf-state/unity_cumulus_lambda/

move:
	 mv /Users/wphyo/Downloads/cumulus_lambda_functions-*.zip tf-module/unity-cumulus/build/cumulus_lambda_functions_deployment.zip

upload_lambda_mcp_dev:
	aws s3 cp tf-module/unity-cumulus/build/cumulus_lambda_functions_deployment.zip s3://uds-dev-cumulus-public/unity_cumulus_lambda/
update_lambda_function_mcp_dev_6:
	aws lambda update-function-code --s3-key unity_cumulus_lambda/cumulus_lambda_functions_deployment.zip --s3-bucket uds-dev-cumulus-public --function-name arn:aws:lambda:us-west-2:237868187491:function:uds-dev-cumulus-metadata_s4pa_generate_cmr --publish &>/dev/null
update_lambda_function_mcp_dev_7:
	aws lambda update-function-code --s3-key unity_cumulus_lambda/cumulus_lambda_functions_deployment.zip --s3-bucket uds-dev-cumulus-public --function-name arn:aws:lambda:us-west-2:237868187491:function:uds-dev-cumulus-metadata_stac_generate_cmr --publish &>/dev/null
update_lambda_function_mcp_dev_auth_list:
	aws lambda update-function-code --s3-key unity_cumulus_lambda/cumulus_lambda_functions_deployment.zip --s3-bucket uds-dev-cumulus-public --function-name arn:aws:lambda:us-west-2:237868187491:function:uds-dev-cumulus-cumulus_auth_list --publish &>/dev/null
update_lambda_function_mcp_dev_auth_add:
	aws lambda update-function-code --s3-key unity_cumulus_lambda/cumulus_lambda_functions_deployment.zip --s3-bucket uds-dev-cumulus-public --function-name arn:aws:lambda:us-west-2:237868187491:function:uds-dev-cumulus-cumulus_auth_add --publish &>/dev/null
update_lambda_function_mcp_dev_auth_delete:
	aws lambda update-function-code --s3-key unity_cumulus_lambda/cumulus_lambda_functions_deployment.zip --s3-bucket uds-dev-cumulus-public --function-name arn:aws:lambda:us-west-2:237868187491:function:uds-dev-cumulus-cumulus_auth_delete --publish &>/dev/null

update_lambda_function_mcp_dev_uds_api:
	aws lambda update-function-code --s3-key unity_cumulus_lambda/cumulus_lambda_functions_deployment.zip --s3-bucket uds-dev-cumulus-public --function-name arn:aws:lambda:us-west-2:237868187491:function:uds-dev-cumulus-uds_api_1 --publish &>/dev/null

update_lambda_function_mcp_sbx_uds_api:
	aws lambda update-function-code --s3-key unity_cumulus_lambda/cumulus_lambda_functions_deployment.zip --s3-bucket uds-dev-cumulus-public --function-name arn:aws:lambda:us-west-2:237868187491:function:uds-sbx-cumulus-uds_api_1 --publish &>/dev/null

mcp_dev: upload_lambda_mcp_dev update_lambda_function_mcp_dev_auth_list update_lambda_function_mcp_dev_auth_add update_lambda_function_mcp_dev_auth_delete

mcp_dev_fastapi: upload_lambda_mcp_dev update_lambda_function_mcp_dev_uds_api

update_lambda_function_mcp_sbx_7:
	aws lambda update-function-code --s3-key unity_cumulus_lambda/cumulus_lambda_functions_deployment.zip --s3-bucket uds-dev-cumulus-public --function-name arn:aws:lambda:us-west-2:237868187491:function:uds-sbx-cumulus-metadata_stac_generate_cmr --publish &>/dev/null

update_lambda_function_mcp_sbx_8:
	aws lambda update-function-code --s3-key unity_cumulus_lambda/cumulus_lambda_functions_deployment.zip --s3-bucket uds-dev-cumulus-public --function-name arn:aws:lambda:us-west-2:237868187491:function:uds-sbx-cumulus-granules_to_es --publish &>/dev/null


update_lambda_function_uds-sbx-cumulus-granules_cnm_response_writer:
	aws lambda update-function-code --s3-key unity_cumulus_lambda/cumulus_lambda_functions_deployment.zip --s3-bucket uds-dev-cumulus-public --function-name arn:aws:lambda:us-west-2:237868187491:function:uds-sbx-cumulus-granules_cnm_response_writer --publish &>/dev/null

update_lambda_function_mcp_sbx_ingester:
	aws lambda update-function-code --s3-key unity_cumulus_lambda/cumulus_lambda_functions_deployment.zip --s3-bucket uds-dev-cumulus-public --function-name arn:aws:lambda:us-west-2:237868187491:function:uds-sbx-cumulus-granules_cnm_ingester --publish &>/dev/null

mcp_sbx: upload_lambda_mcp_dev update_lambda_function_mcp_sbx_7 update_lambda_function_mcp_sbx_8

mcp_sbx_fastapi: upload_lambda_mcp_dev update_lambda_function_mcp_sbx_uds_api
