#!/bin/bash

# ==========================================================
# H-K9 COMMAND CENTER: HIGH-PERFORMANCE LAUNCHER (FINAL)
# Optimized for RTX 4090 / 6000 Ada / A100 / H100
# ==========================================================

echo "🐺 [H-K9] Launching Heart of the Empire..."

# 1. パスの自動特定
PROJECT_ROOT=$(pwd)
COMFYUI_DIR="/workspace/ComfyUI"

# 2. GitHub 同期 (自動競合解決)
echo "🐙 [H-K9] Synchronizing Intelligence..."
git fetch origin main
# ローカルの変更と競合した場合は、GitHub側を優先してクリーンに保つ
git reset --hard origin/main

# 3. GPU/CUDA 12.x 最適化フラグ
export CUDA_LAUNCH_BLOCKING=0
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
# 4090, A100, H100 までの主要GPUをカバー
export TORCH_CUDA_ARCH_LIST="8.0 8.6 8.9 9.0"

# 4. 依存関係のサイレント修復
pip install -q pandas pathlib flask requests opencv-python-headless sageattention xformers

# 5. i2i (改シリーズ) 用のディレクトリ確保
mkdir -p $PROJECT_ROOT/inputs/refer_images
mkdir -p $PROJECT_ROOT/outputs/images

# 6. ComfyUI 起動 (バックグラウンド)
echo "🚀 [H-K9] Launching ComfyUI..."
cd $COMFYUI_DIR
python3 main.py \
    --listen 0.0.0.0 \
    --port 8188 \
    --bf16-storage \
    --use-split-cross-attention \
    --preview-method auto \
    --extra-model-paths-config "$PROJECT_ROOT/core/protocols/extra_model_paths.yaml" > /workspace/comfy_server.log 2>&1 &

# 7. 思想エンジン起動 (インタラクティブ)
echo "🧠 [H-K9] Thought Generator: ONLINE"
echo "----------------------------------------------------------"
echo "Mission: Ready for i2i (KAI-Series) and Generation."
echo "Use 'python3 sync_to_gdrive.py' before termination."
echo "----------------------------------------------------------"

cd $PROJECT_ROOT
# インタラクティブモードで待機
python3 core/engines/thought_generator.py --interactive
