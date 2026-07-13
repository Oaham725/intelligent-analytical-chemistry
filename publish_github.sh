#!/usr/bin/env bash
set -euo pipefail
repo_name="${1:-intelligent-analytical-chemistry}"
gh auth status >/dev/null
owner="$(gh api user --jq .login)"
if ! gh repo view "$owner/$repo_name" >/dev/null 2>&1; then
  gh repo create "$repo_name" --public --source . --remote origin --push
else
  git remote get-url origin >/dev/null 2>&1 || git remote add origin "https://github.com/$owner/$repo_name.git"
  git push -u origin main
fi
gh api --method POST "repos/$owner/$repo_name/pages" -f build_type=workflow >/dev/null 2>&1 || true
echo "Repository: https://github.com/$owner/$repo_name"
echo "Pages: https://$owner.github.io/$repo_name/"
