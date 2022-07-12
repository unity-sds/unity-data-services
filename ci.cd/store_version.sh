#!/usr/bin/env bash
software_version=`python3 ${GITHUB_WORKSPACE}/setup.py --version`
echo $software_version
echo "software_version=${software_version}" >> ${GITHUB_ENV}