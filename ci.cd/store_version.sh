#!/usr/bin/env bash
software_version=`python3 ${GITHUB_WORKSPACE}/setup.py --version`
echo $software_version
echo "software_version=${software_version}" >> ${GITHUB_ENV}
echo "PR_NUMBER1=${github.event.number}" >> ${GITHUB_ENV}
echo "PR_TITLE1=${github.event.pull_request.title}" >> ${GITHUB_ENV}