#!/bin/bash

# === 設定 ===
PROJECT_DIR="/workspace/Project-Dystopia-Core"
REMOTE_NAME="gdrive"
REMOTE_PATH="Dystopia_Full_Backup"

echo "🧬 Project Dystopia: Summoning Memory from $REMOTE_NAME..."

# 1. コアスクリプト・設定・テンプレートの復元
rclone copy "$REMOTE_NAME:$REMOTE_PATH/core" "$PROJECT_DIR/core" --progress --create-empty-src-dirs
rclone copy "$REMOTE_NAME:$REMOTE_PATH/config" "$PROJECT_DIR/config" --progress --create-empty-src-dirs
rclone copy "$REMOTE_NAME:$REMOTE_PATH/workflows" "$PROJECT_DIR/workflows" --progress --create-empty-src-dirs

# 2. 思想ログ・画像・動画・payloadログの復元
rclone copy "$REMOTE_NAME:$REMOTE_PATH/outputs" "$PROJECT_DIR/outputs" --progress --create-empty-src-dirs

# 3. LoRAモデルと訓練データの復元
rclone copy "$REMOTE_NAME:$REMOTE_PATH/lora_outputs" "$PROJECT_DIR/lora_outputs" --progress --create-empty-src-dirs
rclone copy "$REMOTE_NAME:$REMOTE_PATH/training_data" "$PROJECT_DIR/training_data" --progress --create-empty-src-dirs

# 4. マニュアルの復元
rclone copy "$REMOTE_NAME:$REMOTE_PATH/manuals" "$PROJECT_DIR/manuals" --progress --create-empty-src-dirs

echo "✅ Memory restoration complete. You are now ready to resume evolution."
