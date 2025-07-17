#!/usr/bin/env bash
# Script to merge multiple branches into a single branch in a Git repository.
# The target unified branch will be called v.0.2.02
# Usage: ./merge_branches.sh branch1 branch2 [... branchN]

# Exit on error
set -e

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <branch1> <branch2> [... branchN]"
  exit 1
fi

# Target unified branch name
target="v.0.2.02"

# Ensure in git repo
if ! git rev-parse --git-dir > /dev/null 2>&1; then
  echo "Error: Not inside a Git repository."
  exit 1
fi

# Create or checkout target unified branch
git fetch origin
if git show-ref --verify --quiet refs/heads/$target; then
  git checkout $target
elif git ls-remote --heads origin $target | grep -q "$target"; then
  git checkout -b $target origin/$target
else
  git checkout -b $target
fi

# Merge each branch sequentially
for branch in "$@"; do
  echo "\n--- Merging $branch into $target ---"
  # Verify remote branch exists
  if ! git ls-remote --exit-code origin "$branch"; then
    echo "Branch '$branch' not found on remote. Ensure the name is correct."
    exit 1
  fi
  # Fetch branch into local
  git fetch origin "$branch":"$branch"
  # Merge
  if ! git merge --no-ff "$branch" -m "Merge branch '$branch' into $target"; then
    echo "Conflict occurred during merge of $branch. Resolve and then 'git merge --continue'."
    exit 1
  fi
  # Optional: delete local fetched branch
  # git branch -d "$branch"
done

cat << EOF
All branches merged into $target.
Next steps:
  1. Resolve any manual conflicts and run 'git merge --continue'.
  2. Push the unified branch:
       git push -u origin $target
EOF
