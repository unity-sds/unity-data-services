#!/usr/bin/env bash
git status
git diff
current_branch=`git branch --show-current`
git add -u
git commit -m 'chore: update version + change log'
git push origin $current_branch