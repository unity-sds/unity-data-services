#!/usr/bin/env bash
#current_branch=`git branch --show-current`
current_branch='develop-2023-10-02'
temp_branch="chore-version-update"
commit_message="chore: update version + change log"

#git stash
#git checkout -b ${temp_branch}
#git stash pop
#git status
git config --local user.email "wai.phyo@jpl.nasa.gov"
git config --local user.name ${GITHUB_TRIGGERING_ACTOR}
GH_TOKEN='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'
git add -u
git commit -m "${commit_message}"
git push --force origin $temp_branch
result=`gh pr create --base "${current_branch}" --body "NA" --head "${temp_branch}" --title "${commit_message}"`

#echo $result
#pr_number=` | grep -oP '#\K\d+'`
#echo ${pr_number}
#gh pr review $pr_number --approve
#gh pr merge $pr_number --squash --merge
#git branch -D ${temp_branch}

