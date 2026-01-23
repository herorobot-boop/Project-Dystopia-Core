#!/bin/bash

# 1. フォルダへ移動
cd /workspace/Project-Dystopia-Core

# 2. Gitが初期化されていなければ初期化
if [ ! -d ".git" ]; then
    git init
    git remote add origin https://github.com/herorobot-boop/Project-Dystopia-Core.git
    git branch -M main
    echo "🐣 Git initialized and remote added."
fi

# 3. 全ファイルをステージング
git add .

# 4. コミット（メッセージに日時を入れる）
current_time=$(date "+%Y-%m-%d %H:%M:%S")
git commit -m "Update: $current_time"

# 5. 送信
git push -u origin main

echo "🚀 Intelligence synced to GitHub."
