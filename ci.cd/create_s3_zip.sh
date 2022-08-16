#!/usr/bin/env bash

apt-get update -y && apt-get install zip -y

ZIP_NAME='cumulus_lambda_functions_deployment.zip'
project_root_dir=${PWD}
zip_file="${project_root_dir}/$ZIP_NAME" ; # save the result file in current working directory

tmp_proj='/tmp/cumulus_lambda_functions'

source_dir="/usr/local/lib/python3.9/site-packages/"

mkdir -p "$tmp_proj/cumulus_lambda_functions" && \
cd $tmp_proj && \
cp -a "${project_root_dir}/cumulus_lambda_functions/." "$tmp_proj/cumulus_lambda_functions" && \
cp "${project_root_dir}/setup.py" $tmp_proj && \
python3 setup.py install && \
python3 setup.py install_lib && \
python -m pip uninstall boto3 -y && \
python -m pip uninstall botocore -y && \
cd ${source_dir}
rm -rf ${zip_file} && \
zip -r9 ${zip_file} . && \
echo "zipped to ${zip_file}"
