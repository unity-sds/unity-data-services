#!/usr/bin/env bash
software_version=`python3 ${project_root_dir}/setup.py --version`
echo "software_version=${software_version}" >> ${GITHUB_ENV}