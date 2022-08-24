export IMAGE_PREFIX ?= cae-artifactory.jpl.nasa.gov:16001/gov/nasa/jpl/unity
export NAME ?= uds
export VERSION ?= latest


all: build_lambda upload_lambda update_lambda_function build_docker
local: build_lambda upload_lambda update_lambda_function_1 update_lambda_function_2 update_lambda_function_3
build_docker:
	docker build -t "$(IMAGE_PREFIX)/$(NAME):$(VERSION)" -f docker/Dockerfile .

zip_docker:
	docker save "$(IMAGE_PREFIX)/$(NAME):$(VERSION)" | gzip > "$(NAME)__$(VERSION).tar.gz"

build_lambda:
	docker run --rm -v `PWD`:"/usr/src/app/cumulus_lambda_functions":z -w "/usr/src/app/cumulus_lambda_functions" cae-artifactory.jpl.nasa.gov:17001/python:3.9 ci.cd/create_s3_zip.sh

build_lambda_public:
	docker run --rm -v `PWD`:"/usr/src/app/cumulus_lambda_functions":z -w "/usr/src/app/cumulus_lambda_functions" python:3.7 ci.cd/create_s3_zip.sh

upload_lambda:
	aws --profile saml-pub s3 cp cumulus_lambda_functions_deployment.zip s3://am-uds-dev-cumulus-tf-state/unity_cumulus_lambda/
update_lambda_function_1:
	aws --profile saml-pub lambda update-function-code --s3-key unity_cumulus_lambda/cumulus_lambda_functions_deployment.zip --s3-bucket am-uds-dev-cumulus-tf-state --function-name arn:aws:lambda:us-west-2:884500545225:function:am-uds-dev-cumulus-cumulus_collections_dapa --publish &>/dev/null
update_lambda_function_2:
	aws --profile saml-pub lambda update-function-code --s3-key unity_cumulus_lambda/cumulus_lambda_functions_deployment.zip --s3-bucket am-uds-dev-cumulus-tf-state --function-name arn:aws:lambda:us-west-2:884500545225:function:am-uds-dev-cumulus-cumulus_granules_dapa --publish &>/dev/null
update_lambda_function_3:
	aws --profile saml-pub lambda update-function-code --s3-key unity_cumulus_lambda/cumulus_lambda_functions_deployment.zip --s3-bucket am-uds-dev-cumulus-tf-state --function-name arn:aws:lambda:us-west-2:884500545225:function:am-uds-dev-cumulus-cumulus_collections_ingest_cnm_dapa --publish &>/dev/null
