#!/bin/bash

# ==========================================================
# H-K9 COMMAND CENTER: FINAL LAUNCHER (V3)
# ==========================================================

echo "🐺 [H-K9] Initiating Self-Evolving Environment..."

PROJECT_ROOT=$(pwd)
COMFYUI_DIR="/workspace/ComfyUI"

# 1. GitHub 同期
git fetch origin main && git reset --hard origin/main

# 2. 環境変数と最適化
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export TORCH_CUDA_ARCH_LIST="8.0 8.6 8.9 9.0"

# 3. 依存関係の修復
pip install -q pandas pathlib flask requests opencv-python-headless sageattention xformers

# 4. tmux セッションの構築（画面分割）
# セッション名: h_k9
tmux new-session -d -s h_k9

# 左パネル: ComfyUI ログ監視
tmux send-keys -t h_k9 "cd $COMFYUI_DIR && python3 main.py --listen 0.0.0.0 --port 8188 --bf16-storage --extra-model-paths-config $PROJECT_ROOT/core/protocols/extra_model_paths.yaml" C-m

# 右パネル: 思想エンジン + 翻訳レイヤー + 検品
tmux split-window -h -t h_k9
tmux send-keys -t h_k9 "cd $PROJECT_ROOT && python3 core/engines/thought_generator.py --interactive" C-m

# 起動完了の通知
echo "✅ [H-K9] System deployed. Use 'tmux attach-session -t h_k9' to enter command center."
echo "Mission Ready."
