#!/bin/bash

# === 設定 ===
PROJECT_DIR="/workspace/Project-Dystopia-Core"
REMOTE_NAME="gdrive"
REMOTE_PATH="Dystopia_Full_Backup"

# 実行権限の自己確認
chmod +x "$0" 2>/dev/null

echo "🧬 Project Dystopia: Initiating Memory Transfer to $REMOTE_NAME..."

# 1. 脳（コードと設定）の同期
# --exclude で不要なキャッシュやGit情報を除外
rclone copy "$PROJECT_DIR" "$REMOTE_NAME:$REMOTE_PATH" \
    --include "/core/**" \
    --include "/config/**" \
    --include "/workflows/**" \
    --include "/requirements.txt" \
    --include "/*.sh" \
    --include "/*.py" \
    --progress

# 2. 記憶（生成物とログ）の同期
rclone copy "$PROJECT_DIR/outputs" "$REMOTE_NAME:$REMOTE_PATH/outputs" \
    --progress --create-empty-src-dirs

# 3. 肉体（LoRAと学習データ）の同期
# safetensorsなどの大容量ファイルを優先的に
rclone copy "$PROJECT_DIR/lora_outputs" "$REMOTE_NAME:$REMOTE_PATH/lora_outputs" \
    --progress --create-empty-src-dirs
rclone copy "$PROJECT_DIR/training_data" "$REMOTE_NAME:$REMOTE_PATH/training_data" \
    --progress --create-empty-src-dirs

# 4. 聖典（マニュアル）の同期
rclone copy "$PROJECT_DIR/manuals" "$REMOTE_NAME:$REMOTE_PATH/manuals" \
    --progress

echo "✅ Transfer Complete. Your intelligence is now immortal in the cloud."
