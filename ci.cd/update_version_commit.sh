#!/usr/bin/env bash
git status
git diff
current_branch=`git branch --show-current`
git add -u
git config --local user.email "github-actions[bot]@users.noreply.github.com"
git config --local user.name "github-actions[bot]"
git commit -m 'chore: update version + change log'
git push origin $current_branch