#!/bin/bash
# ==========================================================
# H-K9 COMMAND CENTER: FINAL LAUNCHER (V3.1)
# ==========================================================

echo "🐺 [H-K9] Initiating Tactical Environment..."

PROJECT_ROOT="/workspace/Project-Dystopia-Core"
COMFYUI_DIR="/workspace/ComfyUI"

# 1. ワークスペース移動とGitHub同期
cd /workspace
if [ ! -d "$PROJECT_ROOT" ]; then
    git clone https://github.com/herorobot-boop/Project-Dystopia-Core.git
fi
cd $PROJECT_ROOT
git fetch origin main && git reset --hard origin/main

# 2. 依存関係の修復
pip install -q pandas pathlib flask requests opencv-python-headless sageattention xformers

# 3. tmux セッションの構築（画面分割）
tmux kill-session -t h_k9 2>/dev/null
tmux new-session -d -s h_k9

# 左パネル: ComfyUI 起動
tmux send-keys -t h_k9 "cd $COMFYUI_DIR && python3 main.py --listen 0.0.0.0 --port 8188 --bf16-storage --extra-model-paths-config $PROJECT_ROOT/core/protocols/extra_model_paths.yaml" C-m

# 右パネル: 思想エンジン（エラー時に閉じないよう bash を待機させる）
tmux split-window -h -t h_k9
tmux send-keys -t h_k9 "cd $PROJECT_ROOT && (python3 core/engines/thought_generator.py --interactive || echo '⚠️ 起動エラー発生。設定を確認してください。'); bash" C-m

# 完了通知
echo "✅ [H-K9] Deployment Complete."
echo "👉 Command: tmux a -t h_k9"
