#!/usr/bin/env bash

git status
git diff
current_branch=`git branch --show-current`
git add -u
git config --local user.email "wai.phyo@jpl.nasa.gov"
git config --local user.name ${GITHUB_TRIGGERING_ACTOR}
git commit -m 'chore: update version + change log'
git push --force origin $current_branch
