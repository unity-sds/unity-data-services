#!/usr/bin/env bash

apt-get update -y && apt-get install zip -y

# github.job
github_branch=${GITHUB_REF##*/}
software_version_trailing=""
main_branch="main"
if [ "$github_branch" = "$main_branch" ];
then
  software_version=""
else
  software_version_trailing="-${github_branch}-${GITHUB_RUN_ID}"
fi
software_version=`python3 ${project_root_dir}/setup.py --version`
echo "software_version=${software_version}${software_version_trailing}" >> ${GITHUB_ENV}
cat ${GITHUB_ENV}

ZIP_NAME='cumulus_lambda_functions_deployment.zip'
TERRAFORM_ZIP_NAME='terraform_cumulus_lambda_functions_deployment.zip'
TERRAFORM_MARKETPLACE_ZIP_NAME='terraform_marketplace_deployment.zip'
TERRAFORM_ECR_ZIP_NAME='terraform_ecr_deployment.zip'
TERRAFORM_STAC_BR_ZIP_NAME='terraform_stac_br_deployment.zip'

project_root_dir=${GITHUB_WORKSPACE}
zip_file="${project_root_dir}/$ZIP_NAME" ; # save the result file in current working directory
terraform_zip_file="${project_root_dir}/$TERRAFORM_ZIP_NAME" ; # save the result file in current working directory
terraform_marketplace_zip_file="${project_root_dir}/$TERRAFORM_MARKETPLACE_ZIP_NAME" ; # save the result file in current working directory
terraform_ecr_zip_file="${project_root_dir}/$TERRAFORM_ECR_ZIP_NAME" ; # save the result file in current working directory
terraform_stac_br_zip_file="${project_root_dir}/$TERRAFORM_STAC_BR_ZIP_NAME" ; # save the result file in current working directory

source_dir=`python3 -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])'`

cd ${source_dir}
built_time=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
cat <<EOF > ds_version.json
{
  "version": "$software_version",
  "built": "$built_time"
}
EOF
rm -rf ${zip_file} && \
zip -r9 ${zip_file} . && \
echo "zipped to ${zip_file}"

cd ${project_root_dir}/tf-module/unity-cumulus
mkdir build
cp ${zip_file} build/

cd $project_root_dir/tf-module/unity-cumulus
zip -9 ${terraform_zip_file} * **/*

cd $project_root_dir/tf-module/marketplace
zip -9 ${terraform_marketplace_zip_file} * **/*

cd $project_root_dir/tf-module/ds_img_to_ecr
zip -9 ${terraform_ecr_zip_file} * **/*

cd $project_root_dir/tf-module/stac_browser
zip -9 ${terraform_stac_br_zip_file} * **/*


