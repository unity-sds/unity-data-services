#!/usr/bin/env bash
current_branch=`git branch --show-current`
echo "current_branch: ${current_branch}"
#current_branch='develop-2023-10-02'
current_date=$(date +%Y-%m-%dT%H-%M-%S)
temp_branch="chore-version-update--${current_date}"
echo "temp_branch: ${temp_branch}"
commit_message="chore: update version + change log"

env

git stash
git checkout -b ${temp_branch}
git stash pop
git status
echo "setting email and name config"
git config --local user.email "wai.phyo@jpl.nasa.gov"
git config --local user.name ${GITHUB_TRIGGERING_ACTOR}
echo "adding updated files"
git add -u
echo "committing with ${commit_message}"
git commit -m "${commit_message}"
echo "pushing to origin"
git push --force origin $temp_branch
echo "creating PR"
result=`gh pr create --base "${current_branch}" --body "NA" --head "${temp_branch}" --title "${commit_message}"`
echo "PR result $result"
pr_number=`echo $result | grep -oE '[0-9]+$'`
echo "PR number ${pr_number}"
# don't allow auto merge to avoid bad actors using it to merge other code
#gh pr review $pr_number --approve
#echo "merging PR"
#gh pr merge $pr_number --squash --admin
#echo "deleting branch"
#git push origin --delete ${temp_branch}
# mock update
# mock update 6
