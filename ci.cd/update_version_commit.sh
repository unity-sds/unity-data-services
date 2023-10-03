#!/usr/bin/env bash
#current_branch=`git branch --show-current`
current_branch='develop-2023-10-02'
temp_branch="chore-version-update"
commit_message="chore: update version + change log"

env

git stash
git checkout -b ${temp_branch}
git stash pop
git status
git config --local user.email "wai.phyo@jpl.nasa.gov"
git config --local user.name ${GITHUB_TRIGGERING_ACTOR}
git add -u
git commit -m "${commit_message}"
git push --force origin $temp_branch
result=`gh pr create --base "${current_branch}" --body "NA" --head "${temp_branch}" --title "${commit_message}"`
echo $result
pr_number=`echo $result | grep -oE '[0-9]+$'`
echo ${pr_number}
#gh pr review $pr_number --approve
# hi
gh pr merge $pr_number --squash --admin
git push origin --delete ${temp_branch}
