#!/usr/bin/env bash
# 変更をまとめてコミットしてpushする。使い方: bash scripts/sync.sh "追加"
set -euo pipefail

cd "$(dirname "$0")/.."

MSG="${1:-更新}"

if [ ! -d .git ]; then
  echo "gitリポジトリではない。git init するか clone してから実行" >&2
  exit 1
fi

if [ -z "$(git status --porcelain)" ]; then
  echo "変更なし"
  exit 0
fi

git add -A
git commit -m "$MSG"
git push

echo "push完了: $MSG"
