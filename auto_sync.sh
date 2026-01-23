#!/bin/bash
# 30分ごとに GDrive へバックアップを取るバックグラウンド監視スクリプト
while true; do
  echo "📡 Syncing intelligence to Google Drive..."
  rclone copy /workspace/Project-Dystopia-Core gdrive:/Dystopia_Backup/Autosave --exclude "outputs/images/**"
  # 画像は重いため、ログとコードを優先的に同期
  echo "✅ Sync complete. Next sync in 30 minutes."
  sleep 1800
done
